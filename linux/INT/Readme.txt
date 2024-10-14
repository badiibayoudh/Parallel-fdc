Actions:
1- Run the command to execute the orchesration of FDC manually: 
  python3 /applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/ManageFdc.py

2- To change the  configuration, modify the entries in  the file /applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/config.py

Workflow:
Plmxml will be copied to /mounts/import/cdm/VISVIEW/AS-PLM_fdc and the jts to /mounts/import/cdm/geo/jt_fdc/  After the the jts are completely downloaded, the plmxml will be moved to  /mounts/import/cdm/VISVIEW/AS-PLM and then imported.



