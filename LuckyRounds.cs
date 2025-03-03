using MelonLoader;
using BTD_Mod_Helper;
using LuckyRounds;
using Il2CppAssets.Scripts.Models;
using Il2CppAssets.Scripts.Data;

[assembly: MelonInfo(typeof(LuckyRounds.LuckyRounds), ModHelperData.Name, ModHelperData.Version, ModHelperData.RepoOwner)]
[assembly: MelonGame("Ninja Kiwi", "BloonsTD6")]

namespace LuckyRounds;

public class LuckyRounds : BloonsTD6Mod
{
    public override void OnApplicationStart()
    {
        ModHelper.Msg<LuckyRounds>("LuckyRounds loaded!");
    }

    public override void OnNewGameModel(GameModel result)
    {
        base.OnNewGameModel(result);

        if (!Settings.UseLuckyRoundSet) return;

        if (result.roundSet.name == "DefaultRoundSet")
        {
            var luckyRoundSet = GameData.Instance.RoundSetByName("LuckyRounds-LuckyRoundSet");
            if (luckyRoundSet != null)
            {
                result.SetRoundSet(luckyRoundSet);
                MelonLogger.Msg("Using LuckyRounds-LuckyRoundSet");
            }
        }
    }
}