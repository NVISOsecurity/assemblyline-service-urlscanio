# URLScan.io service
This repository is a self-developped Assemblyline service fetching the results of a urlscan.io scan.

This service wouldn't have been possible without having modified the "assemblyline_ui" container to change the filename when submiting an URL.

Here's the steps to be able to use this service :
```bash
sudo docker exec -it full_appliance_al_ui_1 /bin/bash
sed -i 's/("name", None)/("url", None)/g' /var/lib/assemblyline/.local/lib/python3.7/site-packages/assemblyline_ui/api/v4/submit.py
exit
sudo docker restart full_appliance_al_ui_1 /bin/bash
```