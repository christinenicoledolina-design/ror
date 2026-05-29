"""
Compatibility checking service.
Validates that selected components work together.
"""


def check_compatibility(components):
    """
    Takes a list of Component objects and returns:
    { "compatible": bool, "issues": [str], "warnings": [str] }
    """
    issues   = []
    warnings = []

    by_cat = {c.category: c for c in components}

    # Rule 1: CPU + Motherboard socket check
    cpu = by_cat.get("CPU")
    mb  = by_cat.get("Motherboard")
    if cpu and mb:
        intel_cpu = "Intel" in (cpu.brand or "")
        amd_cpu   = "AMD"   in (cpu.brand or "")
        intel_mb  = any(x in (mb.specs or "") for x in ["LGA", "Z790", "B760"])
        amd_mb    = any(x in (mb.specs or "") for x in ["AM5", "AM4", "X670"])
        if intel_cpu and amd_mb:
            issues.append("Intel CPU is not compatible with AM4/AM5 motherboard.")
        if amd_cpu and intel_mb:
            issues.append("AMD CPU is not compatible with LGA/Intel motherboard.")

    # Rule 2: PSU wattage warning for high-end GPU
    gpu = by_cat.get("GPU")
    psu = by_cat.get("PSU")
    if gpu and psu:
        if "4080" in gpu.name or "4090" in gpu.name or "7900" in gpu.name:
            if "650" in (psu.name or "") or "550" in (psu.name or ""):
                warnings.append("PSU may be underpowered for this GPU. Consider 850W+.")

    # Rule 3: RAM DDR version check
    ram = by_cat.get("RAM")
    if mb and ram:
        ddr5_mb  = "DDR5" in (mb.specs or "")
        ddr4_mb  = "DDR4" in (mb.specs or "")
        ddr5_ram = "DDR5" in (ram.specs or ram.name or "")
        ddr4_ram = "DDR4" in (ram.specs or ram.name or "")
        if ddr5_mb and ddr4_ram:
            issues.append("Motherboard requires DDR5 RAM, but DDR4 RAM selected.")
        if ddr4_mb and ddr5_ram:
            issues.append("Motherboard supports DDR4 RAM, but DDR5 RAM selected.")

    return {
        "compatible": len(issues) == 0,
        "issues":     issues,
        "warnings":   warnings,
    }
