## CS460 Computer Networks: **Homework 4**

# Files Included
1. tcp-variants-comparison.cc (adapted version)
2. Homework_4_Report.pdf

# Part 1: Running the simulation
* To run the first set of simulations, run the following commands in the
directory where the ns3 program is located:
  * TCP NewReno (0% error): ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --prefix_name=NewReno_0error --transport_prot=TcpNewReno --duration=500 --error_p=0.0"
  * TCP Cubic (0% error): ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --prefix_name=Cubic_0error --transport_prot=TcpCubic --duration=500 --error_p=0.0"

  * TCP NewReno (5% error): ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --prefix_name=NewReno_5error --transport_prot=TcpNewReno --duration=500 --error_p=0.05"
  * TCP Cubic (5% error): ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --prefix_name=Cubic_5error --transport_prot=TcpCubic --duration=500 --error_p=0.05"

# Part 2: Code modifications
* Modifications are labled in the code as "// MODIFICATION:" followed by details
of the modification made.

1. Updated command-line arguments to accept multiple TCP variants.
2. Updated command-line arguments to include and output directory for output.
3. The TCP variants are assigned to each source node.

# Part 2: Running the adapted version of the simulation
* Important: The updated version requires an output Directory where the
results will placed, please specify the directory path when running the command.

* To run the second set of simulations (using the updated version), run the
following commands in the directory where the ns3 program is located:
  * NewReno vs NewReno: ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --outputDir=specifyDirectory --prefix_name=Reno_vs_Reno --transport_prot=TcpNewReno,TcpNewReno --num_flows=2 --delay=50ms --duration=500"
  * Cubic vs Cubic: ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --outputDir=specifyDirectory --prefix_name=Cubic_vs_Cubic --transport_prot=TcpCubic,TcpCubic --num_flows=2 --delay=50ms --duration=500"
  * NewReno vs Cubic: ./ns3 run tcp-variants-comparison --command-template="%s --tracing=1 --outputDir=specifyDirectory --prefix_name=Reno_vs_Cubic --transport_prot=TcpNewReno,TcpCubic --num_flows=2 --delay=50ms --duration=500"
