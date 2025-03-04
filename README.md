<h1 align="center">
<a href="https://github.com/iXendeRouS/LuckyRounds/releases/latest/download/LuckyRounds.dll">
    <img align="right" alt="Download" height="75" src="https://raw.githubusercontent.com/gurrenm3/BTD-Mod-Helper/master/BloonsTD6%20Mod%20Helper/Resources/DownloadBtn.png">
</a>
LuckyRounds
</h1>

[![Requires BTD6 Mod Helper](https://raw.githubusercontent.com/gurrenm3/BTD-Mod-Helper/master/banner.png)](https://github.com/gurrenm3/BTD-Mod-Helper#readme)  

Replaces randomized freeplay with the best theoretically possible round generation, optimized for cash earned and minimizing BADs.  

**DISCLAIMER:** This might be slightly outdated because there was an update to freeplay generation, but I don't know what changed, so yeah.  

## Explanation  

The freeplay round generation algorithm has two main steps:  
1. Calculate the round’s budget as:  
   
   (4000 × ROUND - 225000) × (1.5 - {some random value between 0 and 1})
    
2. In random order, add each group to the round generation if:  
   - The round is within the group's bounds.  
   - The group's score is less than the remaining budget.  

### What this mod does  
This mod aims to simulate vanilla round generation but with perfect randomness:  

- First, get all groups whose bounds contain the given ROUND.  
- Sort these groups by cash earned per score to maximize cash per round.  
- Iterate over **all** groups and add a group to the round generation if:  
  - Adding the group would not exceed the max budget of **1.5 × budget**.  
  - The group is **guaranteed** (has a score of 1 or 2). This includes groups of BADs.  
  - OR The group is **not a BAD group**.  
- Finally, while the minimum budget of **0.5 × budget** has still not been met:  
  - Add the next best cash-per-score BAD group to the round generation.  

### How this preserves vanilla mechanics  
This ensures that the key properties of vanilla round generation are preserved:  
- A budget of **[0.5 - 1.5] × (4000 × ROUND - 225000)** is filled up with bloon groups.  
- All groups are considered and added if they do not exceed the budget.  

To minimize BAD spawns, we "choose" a budget that can be entirely filled with non-BADs (except for guaranteed BAD groups).  
Non-guaranteed BAD groups are only added if the minimum budget has not been met.  

## FAQs  

### Q1: Could a budget exist such that even guaranteed BAD groups are not chosen?  
Yes! Even with 32-bit float precision affecting budget variation, in most cases, a variation exists that fills the budget completely with non-BAD groups.  
- This means BAD groups could be avoided entirely until **round 1075**, where even the minimum budget **cannot** be fully filled with non-BAD groups.  
- However, I **chose** to include "guaranteed" BAD groups anyway because they are intended to be guaranteed—even though they technically aren't.  
- I want this mod to be **interesting and usable** in challenges like Freeplay CHIMPS, so keeping guaranteed BADs maintains the challenge.  

### Q2: Could all the guaranteed BAD groups generate at the end of a round so they can all be eaten by Legend of the Night? 
- Legend of the Night's black hole ability lasts for **8 seconds**.
- Even if all BAD groups spawned back-to-back, it would still take **22 seconds**.  
- **11 seconds** are FBADs and **11 seconds** are regular BADs.  
- The best you could do is **LOTN** **8/11 seconds** of FBADs and a group of **5x zero-send-time** regular BADs.  
- I **chose not** to group BADs like this because it would make gameplay **less challenging** (even though this mod makes generation easier, you know what I mean).  
- Also, it's **common knowledge** that LOTN abuse is cringe, so yeah.  

### Q3: Could the game actually generate this naturally?  
**Short answer:** No.  

**Long answer:** This mod essentially replaces the vanilla round RNG with an **ideal** one.  
- "Ideal" meaning values generated are actually **independent** of one another.  
- This is a very **reasonable** assumption to make about ideal randomness.  

Unfortunately, the game uses a **linear congruential generator (LCG)** for randomness, which has some drawbacks:  
- Values generated are **not** truly independent.  
- The LCG only works well with **positive 32-bit signed integers**.  

This means the chance of any one of those seeds generating anything **close** to LuckyRounds is basically (but not exactly) **zero**.  
- There’s **nothing preventing** the game from generating a LuckyRoundSet naturally—it's just very, very, **VERY** unlikely.  
- Since LCG randomness **isn't self-independent**, certain groups are **more likely** to generate after specific others, making BAD avoidance impractical.  

So, **long answer:** The specific RNG implementation used by BTD6 makes this kind of generation **extremely unlikely** (read: **basically impossible, but not impossible**).  

## Looking to the future  
- I want to make **group send order within a round randomized** to more closely resemble freeplay.  
- However, I don't know how to **generate a roundset at runtime** (as opposed to pre-generating it with a Python script to create `LuckyRoundSet.cs`).  
- Alternatively, I could **hijack** the actual `FreeplayRoundManager` implementation and edit the freeplay groups directly, but that would take time to figure out.  
- **Adding support for ABR** would be cool and not actually that hard, but I can't be bothered right now.  
