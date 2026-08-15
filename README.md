# Generic Modeling of a Slotneutral UAM Approach at Commercial Airports

This modules contains all the relevant scripts required for the dynamic airspace reconfiguration at Munich Aiport. The work was done as part of my semester thesis with the Chair of Aircraft Design at the Technical University of Munich which in collaboration with other partners in the Airbus Air Mobility Initiative (AMI) AirShuttle Project. It is a follow up on the master thesis: ['Development of a Concept to Generate UAM Trajectories in Terminal Airspace on the Example of Munich Airport'] by Reinisch, F. (2023) and the code structure developed by Reuschling, F. (2022a) ['Basic assumptions for trajectory design: Air Mobility Initiative (AMI)'].

In the next sections I will provide a breakdown of the contents in their folders and their respective functions

## Dynamic_Reconfiguration <a name="dynamic_reconfiguration"></a>

This folder contains a majority of my work on dynamic airspace reconfiguration of the restricted airspace previously defined by Reinisch. A detailed breakdown of the code will be provided later. 

## EDDM_Airspace <a name="eddm_airspace"></a>

This folder contains all the airspace representation script with functions, classes and data for the generation of the restricted airspace that was developed by Reuschling, F. (2022a) and implemented by Reinisch. It is used to generate restricted airspaces for difference wake turbulence separation distances that is later used in the code. 

## Input_Data <a name="input_data"></a>

Contains a number of excel sheets with input data tailored for the implementation of the airspace representation script and the dynamic reconfiguration scripts.

## Misc_Test_Scripts <a name="misc_test_scripts"></a>

Contains miscellanous test scripts used in the final implementation of this work

## Output_Map_Files <a name="output_map_files"></a>

Contains all the output map files generated in the context of this work from the Airspace representation scripts and the dynamic reconfiguration scripts. These will be used for visualization on QGIS and Google Earth Pro for the purpose of documentation.

## Restricted_Areas <a name="restricted_areas"></a> 

Contains all the restricted areas generated from the airspace representation script that are then used in the dynamic reconfiguration


