using BTD_Mod_Helper.Api.Data;
using BTD_Mod_Helper.Api.ModOptions;

namespace LuckyRounds
{
    public class Settings : ModSettings
    {
        public static readonly ModSettingBool UseLuckyRoundSet = new(false)
        {
            description = "Replaces randomised freeplay with the best theoretically possible round generation optimised for cash earned and least BADs."
        };
    }
}