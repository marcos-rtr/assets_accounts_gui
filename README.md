# assets_accounts_gui
1. Get the DataLoader exports: #TODO: screenshots of filters for assets and accounts exports
2. Put the files in the resources directory
3. Run the csv_parser script
4. Pyinstaller creates executables for the OS that is being used (use a Windows machine to output Windoes .exe executables)


Windows Pyinstaller instructions:
1. After following all of the above, open the command prompt and navigate to the directory with the gui.py script
2. Run the following in the command prompt:
    pyinstaller --onefile "gui.py"
   There will now be a dist directory created
3. Create a new directory to send to the a distributor as a zip file and create a new directory inside that one named 'resources'
4. Copy the corresponding distributor files (<distributor_name>_accounts.csv, <distributor_name>_assets.csv) into the newly created 
   resources directory
5. Zip the file and send it to the corresponding distributor
