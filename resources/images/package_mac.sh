#!/bin/sh
# Name ..... : package_mac.sh
# Object ... : Package CalcAl on mac and produce a .dmg file ready to istall by user
# Author ... : MAILLARD Thierry (TMD)
# Ref ...... : http://stackoverflow.com/questions/96882/how-do-i-create-a-nice-looking-dmg-for-mac-os-x-using-command-line-tools
# Date ..... : 16/10/2015 - 18/1/2017
# Modif .... :
# 17/1 : Calculate size of DMG according App size + check return codes

echo 'Get Version of app from CalcAl.ini and modify setup_model.py to create setup.py'
idVersion="Number = "
VERSION=$(grep "${idVersion}" CalcAl.ini | sed "s/${idVersion}//1")
echo "Update version number : ${version} in setup.py"
sed "s/VERSION_NUMBER/${VERSION}/1" setup_model.py > setup.py

STAGING_DIR="./Install"             # we copy all our stuff into this dir
APP_NAME="CalcAl"
VOL_NAME="${APP_NAME}_v${VERSION}"
DMG_TMP="${VOL_NAME}_temp.dmg"
APP_SOURCE="dist/${APP_NAME}.app"
DMG_FINAL="${VOL_NAME}.dmg"
# dmg image must be in 72 * 72 dpi resolution and in same dir than this script
DMG_BACKGROUND_IMG="Background_dmg.png"

echo 'Delete Old stuffs'
rm -rf "${DMG_TMP}" "${STAGING_DIR}" "${DMG_FINAL}" build dist __pycache__ */__pycache__ resources/databases/test

echo "Build Mac app in dist directory ..."
python3 setup.py py2app > /dev/null
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem py2app with script setup.py : STOP"
    exit 1
fi

# copy over the stuff we want in the final disk image to our staging dir
mkdir -p "${STAGING_DIR}"
cp -rpf "${APP_SOURCE}" "${STAGING_DIR}"
# ... cp anything else you want in the DMG - documentation, etc.

echo 'Evaluate Size of DMG (must be larger than app size)'
sizeAppKo=$(du -s "${STAGING_DIR}"  |cut -f 1)
SIZE=$[ ${sizeAppKo}+100 ]
echo "Size calculated for new dmg : ${SIZE} Ko"

echo 'Create the temp DMG file : ${DMG_TMP}'
hdiutil create -srcfolder "${STAGING_DIR}" -volname "${VOL_NAME}" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${SIZE}k "${DMG_TMP}"
cr=$?
if [ $cr -ne 0 ]
then
    echo "Problem creating dmg : STOP"
    exit 1
fi
echo "Created DMG: ${DMG_TMP}"

echo "Mount the disk image, and store the DEVICE name"
DEVICE=$(hdiutil attach -readwrite -noverify "${DMG_TMP}" | \
        egrep '^/dev/' | sed 1q | awk '{print $1}')
echo "DEVICE = ${DEVICE}"
echo "Wait 2s ..."
sleep 2

# add a link to the Applications dir
echo "Add link to /Applications"
pushd /Volumes/"${VOL_NAME}"
ln -s /Applications
popd

# add a background image
echo "mkdir /Volumes/\"${VOL_NAME}\"/.background"
mkdir /Volumes/"${VOL_NAME}"/.background
echo "cp \"${DMG_BACKGROUND_IMG}\" /Volumes/\"${VOL_NAME}\"/.background/"
cp "${DMG_BACKGROUND_IMG}" /Volumes/"${VOL_NAME}"/.background/

# tell the Finder to resize the window, set the background,
#  change the icon size, place the icons in the right position, etc.
echo "Placement image : ${DMG_BACKGROUND_IMG}"
echo '
   tell application "Finder"
     tell disk "'${VOL_NAME}'"
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
sync

echo "Unmount ${DEVICE}"
hdiutil detach "${DEVICE}"
echo "Creating compressed image"
hdiutil convert "./${DMG_TMP}" -format UDZO -imagekey zlib-level=9 -o "${DMG_FINAL}"

echo "Cleaning..."
rm -rf "${DMG_TMP}" "${STAGING_DIR}"
rm -rf dist build setup.py

echo "Compress project, Save it and send ${DMG_FINAL} to user."
