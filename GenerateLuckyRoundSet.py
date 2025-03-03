import json
import random

total_cash = 0

with open("freeplay_data.json") as f:
    freeplay_data = json.load(f)

def calculate_budget(round_num):
    return round_num * 4000 - 225000

BLOON_CASH_VALUES = {
    "Moab": 381, "MoabFortified": 381,
    "DdtCamo": 381, "DdtFortifiedCamo": 381,
    "Bfb": 1525, "BfbFortified": 1525,
    "Zomg": 6101, "ZomgFortified": 6101,
    "Bad": 13346, "BadFortified": 13346,
}

def get_bloon_cash(bloon):
    cash = 0
    
    if "Ceramic" in bloon:
        cash = 95
    elif "Lead" in bloon:
        cash = 7
    else:
        cash = BLOON_CASH_VALUES.get(bloon, 0)
        
    return cash * 0.02

def get_group_cash(group):
    return get_bloon_cash(group["bloon"]) * group["count"]

def get_groups_that_can_gen_on_round(data, round_num):
    valid_groups = []
    for group in data:
        if int(group["score"]) <= 0:
            continue

        for bound in group.get("bounds", []):
            if bound["lowerBounds"] <= round_num <= bound["upperBounds"]:
                valid_groups.append(group)
                break

    # Sort by cash earned per score
    valid_groups.sort(key=lambda g: get_group_cash(g) / g["score"], reverse=True)
    return valid_groups

def get_best_round_gen(round_num):
    global total_cash

    budget = calculate_budget(round_num)
    min_budget = budget * 0.5
    max_budget = budget * 1.5
    current_budget = 0

    possible_groups = get_groups_that_can_gen_on_round(freeplay_data, round_num)
    selected_groups = []
    bad_groups = []

    for group in possible_groups:
        group_score = group["score"]

        if current_budget + group_score > max_budget:
            continue
        
        if group["score"] <= 2:
            selected_groups.append(group)
            current_budget += group_score
            total_cash += get_group_cash(group)
        elif group["bloon"] in ["Bad", "BadFortified"]:
            bad_groups.append(group)
        else:
            selected_groups.append(group)
            current_budget += group_score
            total_cash += get_group_cash(group)

    if current_budget < min_budget:
        for group in bad_groups:
            group_score = group["score"]

            if current_budget + group_score > max_budget:
                continue

            selected_groups.append(group)
            current_budget += group_score
            total_cash += get_group_cash(group)

            if current_budget >= min_budget:
                break

    return selected_groups

def generate_csharp(round_num, groups):
    random.shuffle(groups)
    
    time = 0
    csharp_code = f"        case {round_num - 1}:\n            roundModel.ClearBloonGroups();\n"
    for group in groups:
        csharp_code += f'            roundModel.AddBloonGroup("{group["bloon"]}", {group["count"]}, {time}, {time + group["end"]}); // {group["name"]}\n'
        time += group["end"]
    csharp_code += "    break;\n"
    return csharp_code

csharp_output = "public override void ModifyRoundModels(RoundModel roundModel, int round)\n{\n    base.ModifyRoundModels(roundModel, round);\n\n    switch (round)\n    {\n"

for round_num in range(141, 1001):
    groups = get_best_round_gen(round_num)
    # print(f"round: {round_num} | total cash: {total_cash}")
    csharp_output += generate_csharp(round_num, groups)

csharp_output += "    }\n}"

with open("LuckyRoundSet.cs", "w") as f:
    f.write(csharp_output)

print("C# round generation complete!")
print(f"total cash: {total_cash}")
