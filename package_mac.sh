#!/bin/sh
#################################################
# Name ..... : package_mac.sh
# Object ... : Package CalcAl on mac and produce a .dmg file ready to istall by user
# Author ... : MAILLARD Thierry (TMD)
# Ref ...... : http://stackoverflow.com/questions/96882/how-do-i-create-a-nice-looking-dmg-for-mac-os-x-using-command-line-tools
# Date ..... : 16/10/2016 - 8/5/2017
# Option :
#   -s : to build semi standalone .app : need python already installed
# Usage : package_mac.sh [-s]
#################################################

VERSION="1.0"
echo ""
echo "+++++++++++++++++++++"
echo "$0 version $VERSION"
echo "+++++++++++++++++++++"

semistandalone=""
extDmg=""
if [ $# -eq 0 ]
then
    semistandalone="False"
    extDmg="standalone"
elif [ $# -eq 1 -a $1 == "-s" ]
then
    semistandalone="True"
    extDmg="semi_standalone"
else
cat <<END
Error in parameters :
    Usage :
        $0 : build a standalone .app
        $0 -s : build a semistandalone .app (need python installed on computer)
END
    exit 1
fi

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo 'Update version number in SetupModelMac.py ...'
# Get Version of app from CalcAl.ini and modify SetupModelMac.py to create setup.py
idVersion="Number = "
version=$(grep "${idVersion}" CalcAl.ini | sed "s/${idVersion}//1")
echo "Update version number : ${version} in setup.py..."
sed -e "s/VERSION_NUMBER/${version}/1" \
    -e "s/SEMI_STANDALONE/${semistandalone}/1" \
    SetupModelMac.py > setup.py
echo 'setup.py created'
VOLNAME="CalcAl_v${version}"

APP_NAME="CalcAl"
DMG_TMP="pack.temp.dmg"
APP_BUILD="dist/${APP_NAME}.app"
DMG_FINAL_NAME="../CalcAl_${version}_${extDmg}.dmg"
PATH_BACKGROUND_IMG="resources/images/Background_dmg.png"

echo ""
echo "============================="
echo "Start packaging"
if [ ${semistandalone} = "True" ]
then
    echo "Warning semi standalone .app version : need python installed on user computer."
else
    echo "Standalone .app will be built."
fi

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Cleaning..."
rm -rf ${DMG_FINAL_NAME} ${DMG_TMP} build dist __pycache__ */__pycache__ resources/databases/test
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem cleaning : STOP"
    exit 1
fi
echo "OK : Cleaning done."

echo ""
echo "============================="
echo "Building Mac app in dist directory"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Creating application ${APP_BUILD} ..."
python3 setup.py py2app > /dev/null
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem py2app with script setup.py : STOP"
    exit 1
fi
echo "OK : Mac app built in dist directory."

echo ""
echo "============================="
echo "Build R/W DMG ${DMG_TMP}"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Evaluating Size of ${APP_BUILD} for DMG (must be larger than app size)..."
# Don't uderstand unit used but it works
unset BLOCKSIZE
sizeAppKo=$(du -s ${APP_BUILD}  |cut -f 1)
size=$[ ${sizeAppKo}+100 ]
echo "Size calculated for new dmg : ${size} Ko"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Creating DMG : ${DMG_TMP}..."
hdiutil create -srcfolder ${APP_BUILD} -volname ${VOLNAME} -fs HFS+ \
        -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${size}k ${DMG_TMP}
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem creating dmg : STOP"
    exit 1
fi
echo "OK : DMG Created : ${DMG_TMP}"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Mount the disk image, and store the device name"
device=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_TMP}" | \
        egrep '^/dev/' | sed 1q | awk '{print $1}')
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem creating device : STOP"
    exit 1
fi
echo "OK : device created: ${device}"

# Unuseful ???
#echo "Wait 2s"
#sleep 2

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
# add a link to the Applications dir
echo "Add symbolic link to /Applications in /Volumes/${VOLNAME}..."
ln -s /Applications /Volumes/${VOLNAME}/Applications
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem creating symbolic link to /Applications in /Volumes/${VOLNAME} : STOP"
    exit 1
fi
echo "OK : Symbolic link created in /Applications in /Volumes/${VOLNAME}"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Inserting background picture ${PATH_BACKGROUND_IMG} in dmg ..."
# dmg image must be in 72 * 72 dpi resolution
DMG_BACKGROUND_IMG=$(basename ${PATH_BACKGROUND_IMG})
mkdir /Volumes/${VOLNAME}/.background
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem creating dir /Volumes/${VOLNAME}/.background : STOP"
    exit 1
fi
cp ${PATH_BACKGROUND_IMG} /Volumes/${VOLNAME}/.background/
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem inserting ${PATH_BACKGROUND_IMG} in /Volumes/${VOLNAME}/.background : STOP"
    exit 1
fi
echo "OK : ${PATH_BACKGROUND_IMG} Inserted in /Volumes/${VOLNAME}/.background."

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
# tell the Finder to resize the window, set the background,
#  change the icon size, place the icons in the right position, etc.
#Be carefull to quotes in names
echo "Organize DMG : setting background and icon position..."
echo '
tell application "Finder"
tell disk "'${VOLNAME}'"
open
set current view of container window to icon view
set toolbar visible of container window to false
set statusbar visible of container window to false
set the bounds of container window to {400, 100, 920, 440}
set viewOptions to the icon view options of container window
set arrangement of viewOptions to not arranged
set icon size of viewOptions to 72
set background picture of viewOptions to file ".background:'${DMG_BACKGROUND_IMG}'"
set position of item "'${APP_NAME}'.app" of container window to {160, 205}
set position of item "Applications" of container window to {360, 205}
set position of item ".background" of container window to {600, 200}
set position of item ".fseventsd" of container window to {600, 200}
close
open
update without registering applications
delay 2
end tell
end tell
' | osascript
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem setting background and icon position : STOP"
    exit 1
fi
echo "OK : background and icon position"

sync

echo ""
echo "================="
echo "Finializing DMG"

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Changing permission permissions in /Volumes/${VOLNAME}."
chmod -Rf go-w /Volumes/${VOLNAME}
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem changing permissions : STOP"
    exit 1
fi
echo "OK : permissions in /Volumes/${VOLNAME} changed."

sync
echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Closing device ${device}...."
hdiutil detach ${device}
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem Closing device : STOP"
    exit 1
fi
echo "OK : Device ${device} closed...."

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Compressing ${DMG_TMP} to ${DMG_FINAL_NAME}...."
echo "23/3/2017 : Incorporate certificates"
hdiutil convert ${DMG_TMP} -format UDZO -imagekey zlib-level=9 -o ${DMG_FINAL_NAME} \
-certificate /Users/thierry/Documents/clés_PGP/certif_tmd.der \
-cacert /Users/thierry/Documents/clés_PGP/ca.crt
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem Compressing ${DMG_TMP} to ${DMG_FINAL_NAME} : STOP"
    exit 1
fi
echo "OK : ${DMG_FINAL_NAME} created."

echo ""
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Cleaning..."
rm -rf ${DMG_TMP} build dist __pycache__ */__pycache__ setup.py
cr=$?
if [ $cr -ne 0 ]
then
echo "Problem cleaning : STOP"
exit 1
fi
echo "OK : cleaned."

echo ""
echo "============================="
echo "SUCCESS : END packaging in ${DMG_FINAL_NAME}"
ls -l ${DMG_FINAL_NAME}
if [ ${semistandalone} = "True" ]
then
echo "Warning semi standalone .app version : need python installed on user computer."
else
echo "Standalone .app has been built."
fi
echo "Compress source directory $(basename $(pwd)) and save it"
echo "Send ${DMG_FINAL_NAME} to users."
echo "============================="
