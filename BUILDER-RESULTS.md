# Plugin Builder Results

Congratulations! You just built a plugin for QGIS!

Your plugin **SGBTools** was created in: ```/home/mota/vscode/QGIS-Plugins/sgbtools```

Your QGIS plugin directory is located at: ```/home/mota/.local/share/QGIS/QGIS3/profiles/default/python/plugins```


## What's Next

1. Test the generated sources using **make test** (or run tests from your IDE)
2. Copy the entire directory containing your new plugin to the QGIS plugin directory (see Notes below)
3. Test the plugin by enabling it in the QGIS plugin manager and enabling the provider in the Processing Options
4. Customize it by editing the implementation file  ```sgbtools_algorithm.py```


## Notes:

- You can use the **Makefile** to compile and deploy when you make changes. This requires GNU make (gmake). The Makefile is ready to use, however you will have to edit it to add addional Python source files, dialogs, and translations.

- You can also use **pb_tool** to compile and deploy your plugin. Tweak the *pb_tool.cfg* file included with your plugin as you add files. Install **pb_tool** using *pip* or *easy_install*. See [http://loc8.cc/pb_tool](http://loc8.cc/pb_tool) for more information.

For information on writing PyQGIS code, see [http://loc8.cc/pyqgis_resources](http://loc8.cc/pyqgis_resources) for a list of resources.

For more information, see the PyQGIS Developer Cookbook at:
http://www.qgis.org/pyqgis-cookbook/index.html

&copy;2011-2018 GeoApt LLC - geoapt.com 
