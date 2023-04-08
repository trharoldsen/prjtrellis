from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    ("R6C17", "EBR0", FuzzConfig(job="EBROUTE0", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                                 tiles=["EBR_R6C17:EBR0", "EBR_R6C18:EBR1", "EBR_R6C19:EBR2"])),
]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(mode, settings, muxes = None):
            ebrloc = loc
            if mode == "NONE":
                # easier to move EBR out the way than remove it
                ebrloc = "R6C20"
                mode = "PDPW8KC"
            if mode == "PDPW8KC" and "DATA_WIDTH_R" not in settings:
                settings["DATA_WIDTH_R"] = "9"
            if mode == "PDPW8KC" and "DATA_WIDTH_W" not in settings:
                settings["DATA_WIDTH_W"] = "18"
            if mode == "PDPW8KC" and "CSDECODE_W" not in settings:
                settings["CSDECODE_W"] = "0b111"
            if mode == "PDPW8KC" and "CSDECODE_R" not in settings:
                settings["CSDECODE_R"] = "0b111"
            if mode == "DP8KC" and "CSDECODE_A" not in settings:
                settings["CSDECODE_A"] = "0b111"
            if mode == "DP8KC" and "CSDECODE_B" not in settings:
                settings["CSDECODE_B"] = "0b111"
            if mode == "FIFO8KB" and "DATA_WIDTH_R" not in settings:
                settings["DATA_WIDTH_R"] = "9"
            if mode == "FIFO8KB" and "DATA_WIDTH_W" not in settings:
                settings["DATA_WIDTH_W"] = "9"
            if mode == "FIFO8KB" and "CSDECODE_W" not in settings:
                settings["CSDECODE_W"] = "0b11"
            if mode == "FIFO8KB" and "CSDECODE_R" not in settings:
                settings["CSDECODE_R"] = "0b11"
            setting_text = ",".join(["{}={}".format(k, v) for k, v in settings.items()])
            if muxes is not None:
                setting_text += ":" + ",".join(["{}={}".format(k, v) for k, v in muxes.items()])
            return dict(loc=ebrloc, mode=mode, settings=setting_text)

        def get_muxval(sig, val):
            if val == sig:
                return None
            elif val == "INV":
                return {sig: "#INV"}
            else:
                assert False
        loc, ebr, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "ebr.ncl"

#        nonrouting.fuzz_enum_setting(cfg, "{}.CLKAMUX".format(ebr), ["CLKA", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("CLKA", x)), empty_bitfile)
#        nonrouting.fuzz_enum_setting(cfg, "{}.CLKBMUX".format(ebr), ["CLKB", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("CLKB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.RSTAMUX".format(ebr), ["RSTA", "INV"],
                                     lambda x: get_substs("DP8KC", {}, get_muxval("RSTA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.RSTBMUX".format(ebr), ["RSTB", "INV"],
                                     lambda x: get_substs("DP8KC", {}, get_muxval("RSTB", x)), empty_bitfile)
#        nonrouting.fuzz_enum_setting(cfg, "{}.OCEAMUX".format(ebr), ["OCEA", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("OCEA", x)), empty_bitfile)
#        nonrouting.fuzz_enum_setting(cfg, "{}.OCEBMUX".format(ebr), ["OCEB", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("OCEB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.WEAMUX".format(ebr), ["WEA", "INV"],
                                     lambda x: get_substs("DP8KC", {}, get_muxval("WEA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.WEBMUX".format(ebr), ["WEB", "INV"],
                                     lambda x: get_substs("DP8KC", {}, get_muxval("WEB", x)), empty_bitfile)
#        nonrouting.fuzz_enum_setting(cfg, "{}.CEAMUX".format(ebr), ["CEA", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("CEA", x)), empty_bitfile)
#        nonrouting.fuzz_enum_setting(cfg, "{}.CEBMUX".format(ebr), ["CEB", "INV"],
#                                     lambda x: get_substs("DP8KC", {}, get_muxval("CEB", x)), empty_bitfile)
#
        nonrouting.fuzz_enum_setting(cfg, "{}.FIFO8KB.FULLIMUX".format(ebr), ["FULLI", "INV"],
                                     lambda x: get_substs("FIFO8KB", {}, get_muxval("FULLI", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.FIFO8KB.EMPTYIMUX".format(ebr), ["EMPTYI", "INV"],
                                     lambda x: get_substs("FIFO8KB", {}, get_muxval("EMPTYI", x)), empty_bitfile)

        for p in ("A", "B"):
            for i in range(2 if p == "A" else 1):
               sig = "AD{}{}".format(p, i)
               nonrouting.fuzz_enum_setting(cfg, "{}.{}MUX".format(ebr, sig), [sig, "INV"],
                                        lambda x: get_substs("DP8KC", {}, get_muxval(sig, x)), empty_bitfile)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
