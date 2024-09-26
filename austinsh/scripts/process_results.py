def process_results(buses, v_solution):
    print("\nBus\tVoltage Magnitude\tAngle")
    print("======================================")
    for elem in buses:
        elem.final_bus_properties(v_solution)
        print(f"{elem.Bus}\t{elem.mag_v:<.3f}\t\t\t{elem.ang_deg:<.3f}")