#!/bin/sh
# Name ..... : package_mac.sh
# Object ... : Package CalcAl on mac and produce a .dmg file ready to istall by user
# Author ... : MAILLARD Thierry (TMD)
# Ref ...... : http://stackoverflow.com/questions/96882/how-do-i-create-a-nice-looking-dmg-for-mac-os-x-using-command-line-tools
# Date ..... : 16/10/2015 - 13/11/2016
# Modif .... :

cd /Users/thierry/Documents/dietetique/CalcAl
echo "Build Mac app in dist directory"
rm -rf build dist __pycache__ */__pycache__
python3 setup.py py2app

echo "Build R/W DMG pack.temp.dmg"
title="CalcAl"
source="dist/Calcal.app"
# It must be larger than the result will be.
# In this example, the bash variable "size" contains the size in Kb
# Size must be greater than size of app in Ko
size=2500
hdiutil create -srcfolder "${source}" -volname "${title}" -fs HFS+ \
        -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${size}k pack.temp.dmg

echo "Mount the disk image, and store the device name"
device=$(hdiutil attach -readwrite -noverify -noautoopen "pack.temp.dmg" | \
        egrep '^/dev/' | sed 1q | awk '{print $1}')

echo "Wait 5s"
sleep 5

echo "Insert background picture (PB)"
#set background picture of theViewOptions to file ".background:${backgroundPictureName}"
# gives error ???
#412:499: execution error: Erreur dans Finder : Il est impossible de régler
#file ".background:${backgroundPictureName}" of disk "CalcAl" à
#file ".background:${backgroundPictureName}" of disk "CalcAl". (-10006)
# Problème with permissions on .Trashes in .dmg ???
# TODO : see using https://github.com/andreyvit/create-dmg

#backgroundPictureName = "resources/images/logo_about.png"
#echo '
#tell application "Finder"
#tell disk "'${title}'"
#open
#set current view of container window to icon view
#set toolbar visible of container window to false
#set statusbar visible of container window to false
#set the bounds of container window to {400, 100, 885, 430}
#set theViewOptions to the icon view options of container window
#set arrangement of theViewOptions to not arranged
#set icon size of theViewOptions to 72
#set background picture of theViewOptions to file ".background:'${backgroundPictureName}'"
#make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
#set position of item "'${applicationName}'" of container window to {100, 100}
#set position of item "Applications" of container window to {375, 100}
#update without registering applications
#delay 5
#close
#end tell
#end tell
#' | osascript
echo "TODO : solve errors with background"

echo "Finialize the DMG : permissions, compressing and releasing it"
dmgName="CalcAl.dmg"
chmod -Rf go-w /Volumes/"${title}"
sync
sync
hdiutil detach ${device}
hdiutil convert "./pack.temp.dmg" -format UDZO -imagekey zlib-level=9 -o "dist/${dmgName}"
mv dist/${dmgName} .

echo "Cleaning..."
rm -rf ./pack.temp.dmg build dist __pycache__ */__pycache__

echo "Compress project, Save it and send ${dmgName} to user."
