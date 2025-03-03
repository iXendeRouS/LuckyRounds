import json
import random

initial_cash = 309251
total_cash = initial_cash  # Start with the initial cash

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
    round_cash = 0  # Track cash for this round only

    for group in possible_groups:
        group_score = group["score"]

        if current_budget + group_score > max_budget:
            continue
        
        if group["score"] <= 2:
            selected_groups.append(group)
            current_budget += group_score
            group_cash = get_group_cash(group)
            round_cash += group_cash
        elif group["bloon"] in ["Bad", "BadFortified"]:
            bad_groups.append(group)
        else:
            selected_groups.append(group)
            current_budget += group_score
            group_cash = get_group_cash(group)
            round_cash += group_cash

    if current_budget < min_budget:
        for group in bad_groups:
            group_score = group["score"]

            if current_budget + group_score > max_budget:
                continue

            selected_groups.append(group)
            current_budget += group_score
            group_cash = get_group_cash(group)
            round_cash += group_cash

            if current_budget >= min_budget:
                break

    total_cash += round_cash  # Add this round's cash to total
    return selected_groups

def generate_csharp(round_num, groups):
    random.shuffle(groups)
    
    time = 0
    csharp_code = f"            case {round_num - 1}:\n                roundModel.ClearBloonGroups();\n"
    for group in groups:
        csharp_code += f'                roundModel.AddBloonGroup("{group["bloon"]}", {group["count"]}, {time}, {time + group["end"]}); // {group["name"]}\n'
        time += group["end"]
    csharp_code += "                break;\n"
    return csharp_code

# Start of the file with all the necessary imports and class definition
file_header = """using MelonLoader;
using BTD_Mod_Helper;
using LuckyRounds;
using Il2CppAssets.Scripts.Models;
using Il2CppAssets.Scripts.Data;
using BTD_Mod_Helper.Api.Bloons;
using BTD_Mod_Helper.Api.Enums;
using Il2CppAssets.Scripts.Models.Rounds;
using BTD_Mod_Helper.Extensions;

[assembly: MelonInfo(typeof(LuckyRounds.LuckyRounds), ModHelperData.Name, ModHelperData.Version, ModHelperData.RepoOwner)]
[assembly: MelonGame("Ninja Kiwi", "BloonsTD6")]

namespace LuckyRounds;

public class LuckyRoundSet : ModRoundSet
{
    public override string BaseRoundSet => RoundSetType.Default;
    public override int DefinedRounds => 1000;
    public override string DisplayName => "Lucky Rounds";
    public override string Icon => VanillaSprites.Alchemist050;

    public override void ModifyRoundModels(RoundModel roundModel, int round)
    {
        base.ModifyRoundModels(roundModel, round);

        switch (round)
        {
"""

# End of the file with proper closing brackets
file_footer = """        }
    }
}
"""

csharp_output = file_header

# Dictionary to store cash for each round
cash_by_round = {}
# Dictionary to store bloon groups for each round
rounds_data = {}

for round_num in range(141, 1001):
    groups = get_best_round_gen(round_num)
    cash_by_round[str(round_num)] = round(total_cash, 2)  # Store total cash after this round
    
    # Create round data entry
    round_groups = []
    random.shuffle(groups)  # Shuffle groups to match the C# output
    time = 0
    
    for group in groups:
        round_group = {
            "bloon": group["bloon"],
            "count": group["count"],
            "startTime": time,
            "endTime": time + group["end"],
            "name": group["name"]
        }
        round_groups.append(round_group)
        time += group["end"]
    
    rounds_data[str(round_num)] = round_groups
    
    csharp_output += generate_csharp(round_num, groups)

csharp_output += file_footer

with open("LuckyRoundSet.cs", "w") as f:
    f.write(csharp_output)

# Write the cash.json file
with open("cash.json", "w") as f:
    json.dump(cash_by_round, f, indent=2)

# Write the rounds.json file
with open("rounds.json", "w") as f:
    json.dump(rounds_data, f, indent=2)

print("C# round generation complete!")
print(f"Total cash: {total_cash}")
print("Cash by round data written to cash.json")
print("Round bloon data written to rounds.json")
print("Complete LuckyRoundSet.cs file generated")