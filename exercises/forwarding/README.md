# Implementing Forwarding

This exercise implements IPv4 forwarding. With IPv4 forwarding, the switch 
must perform the following actions for every packet: (i) update the source 
and destination MAC addresses, (ii) decrement the time-to-live (TTL) in the 
IP header, and (iii) forward the packet out the appropriate port.

Each switch will have a single table, which the control plane will populate 
with rules. Each rule will map an IP address to the MAC address and output 
port for the next hop.

We will use the following topology for this exercise. It is a single pod of 
a fat-tree topology and is henceforth referred to as pod-topo:
![pod-topo](./pod-topo.png)

## The P4 Program

The P4 program that will be compiled and installed on the switches is specified 
in [forwarding.p4](./forwarding.p4). We have looked at different components of 
this program in the lectures: how to define the headers, defining parsers,
control blocks, and deparsers. 

Spend some time to study this program and these components. We will extend this
program in the next exercise ([filter](../filter)) with more functionality. 

Note that our P4 program will be written for the V1Model architecture implemented
on P4.org's bmv2 software switch. The architecture file for the V1Model
can be found at: /usr/local/share/p4c/p4include/v1model.p4. This file
describes the interfaces of the P4 programmable elements in the architecture,
the supported externs, as well as the architecture's standard metadata
fields. 

# The Switch:  Implement L3 forwarding
The forwarding.p4 file contains a skeleton P4 program with key pieces of logic replaced by TODO comments. Your implementation should follow the structure given in this file---replace each TODO with logic implementing the missing piece.

A complete forwarding.p4 will contain the following components:

1. Header type definitions for Ethernet (ethernet_t) and IPv4 (ipv4_t).
2. **TODO:** Parsers for Ethernet and IPv4 that populate ethernet_t and ipv4_t fields.
3. An action to drop a packet, using mark_to_drop().
4. **TODO:** An action (called ipv4_forward) that:
    1. Sets the egress port for the next hop.
    2. Updates the ethernet destination address with the address of the next hop.
    3. Updates the ethernet source address with the address of the switch.
    4. Decrements the TTL.
5. **TODO:** A control that:
    1. Defines a table that will read an IPv4 destination address, and invoke either drop or ipv4_forward.
    2. An apply block that applies the table.
6. **TODO:** A deparser that selects the order in which fields are inserted into the outgoing packet.
7. A package instantiation supplied with the parser, control, and deparser.
  > In general, a package also requires instances of checksum verification and recomputation controls. These are not necessary for this tutorial and are replaced with instantiations of empty controls.

## The Controller

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. In this case,
[mycontroller.py](./mycontroller.py) implements our control plane.

The controller is implemented in python and uses P4 Runtime to communicate with the switch. 
You can see examples of how the helper libraries in the `p4runtime_lib` [directory](../../utils/p4runtime_lib)
are used to install rules in the `ipv4_exact` table.

Note that the P4 program also defines the interface between the
switch pipeline and control plane. This interface is defined in the
`forwarding.p4info` file, which will be available in the `build` 
folder after the program is compiled (see the instructions in "Running the exercise").
The table entries that you build in `mycontroller.py`
refer to specific tables, keys, and actions by name, and we use a P4Info helper
to convert the names into the IDs that are required for P4Runtime. Any changes
in the P4 program that add or rename tables, keys, or actions will need to be
reflected in your table entries.

As mentioned above, in `mycontroller.py` you will come across some of the classes and methods in
the `p4runtime_lib` directory. Here is a summary of each of the files in the directory:
- `helper.py`
  - Contains the `P4InfoHelper` class which is used to parse the `p4info` files.
  - Provides translation methods from entity name to and from ID number.
  - Builds P4 program-dependent sections of P4Runtime table entries.
- `switch.py`
  - Contains the `SwitchConnection` class which grabs the gRPC client stub, and
    establishes connections to the switches.
  - Provides helper methods that construct the P4Runtime protocol buffer messages
    and makes the P4Runtime gRPC service calls.
- `bmv2.py`
  - Contains `Bmv2SwitchConnection` which extends `SwitchConnections` and provides
    the BMv2-specific device payload to load the P4 program.
- `convert.py`
  - Provides convenience methods to encode and decode from friendly strings and
    numbers to the byte strings required for the protocol buffer messages.
  - Used by `helper.py`

Spend some time to review this program. In the next exercise ([filter](../filter)),
we will extend this program to install rules in other tables in the switch.

## Mininet

Mininet is a network emulation environment. It uses network namespaces to 
creates a realistic virtual network, running real kernel, switch and application code,
on a single machine.

You do not need to know the details of mininet to finish this assignment, but,
if interested, you can find more information about mininet [here](https://mininet.org/)

## Running the exercise

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `forwarding.p4`,
   * start a Mininet instance with four switches (`s1`, `s2`, `s3`, `s4`)
     configured as shown in the pod topology, each connected to one host 
     (`h1`, `h2`, `h3`, `h4`), and
   * assign IPs of `10.0.1.1`, `10.0.2.2`, `10.0.3.3`, and `10.0.4.4` to the respective hosts.

2. You should now see a Mininet command prompt. Start a ping between h1 and h2:
   ```bash
   mininet> h1 ping h2
   ```
   Because there are no rules on the switches, you should **not** receive any
   replies yet. You should leave the ping running in this shell.

3. Open another shell and run the controller:
   ```bash
   cd ~/P4-excercise/exercises/forwarding
   ./mycontroller.py
   ```
   This will install the `forwarding.p4` program on the switches and push the
   forwarding rules. You should now see the pings in the other shell completing
   successfully. 
   
4. Press `Ctrl-D` or enter `exit` at the mininet prompt to stop Mininet.


## Potential Issues

If you see the following error message when running `mycontroller.py`, then
the gRPC server is not running on one or more switches.

```
p4@p4:~/P4-excercise/exercises/p4runtime$ ./mycontroller.py
...
grpc._channel._Rendezvous: <_Rendezvous of RPC that terminated with (StatusCode.UNAVAILABLE, Connect Failed)>
```

You can check to see which of gRPC ports are listening on the machine by running:
```bash
sudo netstat -lpnt
```

The easiest solution is to enter `Ctrl-D` or `exit` in the `mininet>` prompt,
and re-run `make run`.

## Cleaning up Mininet

If the Mininet shell crashes, it may leave a Mininet instance
running in the background. Use the following command to clean up:
```bash
make clean
```


## Relevant Documentation

The documentation for P4_16 and P4Runtime is available [here](https://p4.org/specs/)

All excercises in this repository use the v1model architecture, the documentation for which is available at:
1. The BMv2 Simple Switch target document accessible [here](https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md) talks mainly about the v1model architecture.
2. The include file `v1model.p4` has extensive comments and can be accessed [here](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).
