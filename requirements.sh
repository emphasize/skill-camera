# The requirements.sh is an advanced mechanism and should rarely be needed.
# Be aware that it won't run with root permissions and 'sudo' won't work
# in most cases.  Py msm handles invokes the script with sudo internally if the platform allows it

#detect distribution using lsb_release (may be replaced parsing /etc/*release)
#TODO until Pako is up to speed
function os_is() {
    [[ $(grep "^ID=" /etc/os-release | awk -F'=' '/^ID/ {print $2}' | sed 's/\"//g') == $1 ]]
}

function os_is_like() {
    grep "^ID_LIKE=" /etc/os-release | awk -F'=' '/^ID_LIKE/ {print $2}' | sed 's/\"//g' | grep -q "\\b$1\\b"
}

function found_exe() {
    hash "$1" 2>/dev/null
}

mycroft_path=$( dirname $VIRTUAL_ENV )
openvc_path="opencv"
working_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

dependencies=( python-opencv )

# default pm
pm="sudo apt-get install -y"

#setting dependencies and package manager in relation to the distribution
#Todo Use Pako if Pako set flags appropriately (eg -y or --needed)
if os_is_like arch || os_is arch; then
    pm="sudo pacman -Sy --needed"
    dependencies=( opencv )
elif os_is_like debian || os_is debian || os_is_like ubuntu || os_is ubuntu || os_is linuxmint || os_is antiX; then
    pm="sudo apt-get install -y"
    dependencies=( libaom0 libatk-bridge2.0-0 libatk1.0-0 libatlas3-base libatspi2.0-0 libavcodec58 libavformat58 libavutil56 libbluray2 libcairo-gobject2 libcairo2 libchromaprint1 libcodec2-0.8.1 libcroco3 libdatrie1 libdrm2 libepoxy0 libfontconfig1 libgdk-pixbuf2.0-0 libgfortran5 libgme0 libgraphite2-3 libgsm1 libgtk-3-0 libharfbuzz0b libilmbase23 libjbig0 libmp3lame0 libmpg123-0 libogg0 libopenexr23 libopenjp2-7 libopenmpt0 libopus0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 librsvg2-2 libshine3 libsnappy1v5 libsoxr0 libspeex1 libssh-gcrypt-4 libswresample3 libswscale5 libthai0 libtheora0 libtiff5 libtwolame0 libva-drm2 libva-x11-2 libva2 libvdpau1 libvorbis0a libvorbisenc2 libvorbisfile3 libvpx5 libwavpack1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libwebp6 libwebpmux3 libx264-155 libx265-165 libxcb-render0 libxcb-shm0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxinerama1 libxkbcommon0 libxrandr2 libxrender1 libxvidcore4 libzvbi0 )
elif found_exe pkcon; then
    pm="pkcon install"
elif os_is_like fedora || os_is fedora || os_is rhel || os_is centos; then
    dependencies=( numpy opencv* )
    pm="sudo yum -y install"
fi

# installing dependencies
for dep in "${dependencies[@]}"
do
    echo "installing: $dep"
    $pm $dep
done

if [[  $( uname -m ) == *"arm"* ]] && [[ -z $( os_is raspbian ) ]]; then
    if [[ -z $( pip freeze | grep opencv-python= ) ]] ; then
        cd ~
        mkdir $path
        cd $path
        echo "OpenCV Python has to be build from source on ARM Architectures (not running RaspiOS/Raspbian)"
        git clone --recursive https://github.com/skvark/opencv-python.git
        echo 'Warning: This will take a really long time (up to 2 hours).'
        echo '         The following build process will run without extra flags'
        echo '         If you want to run it with custom flags choose N'
        echo
        echo 'Continue (or build yourself)? y/N'
        read -n1 continue
        if [[ $continue != 'y' ]] ; then
            #Todo don't know if this can be run consecutively
            cd opencv-python
            #build opencv-python
            pip wheel . --verbose
            ${mycroft_path}/bin/mycroft-pip install opencv_python*.whl
            if ! $( pip freeze | grep opencv-contrib-python= ) ; then
                #build opencv-python-contrib
                export ENABLE_CONTRIB=1
                pip wheel . --verbose
                ${mycroft_path}/bin/mycroft-pip install opencv_contrib_python*.whl
            fi
            echo
            echo "The wheels are stored in ~/$path"
            echo 'install it with mycroft-pip install <wheel>'
        else
          echo "The opencv-python git was cloned to ~/$path"
          echo 'Please visit https://github.com/skvark/opencv-python for further information on the manual build process'
        fi
    fi
fi

#bring in some preconfiguration to ~/.mycroft/mycroft.conf
JSON=$( cat ~/.mycroft/mycroft.conf | jq '.cams = { "picture_path": "'$HOME'/webcam/", "camera_sound": "'$working_path'/camera.wav", "examplecam": "exampleurl" }' )
echo "$JSON" > ~/.mycroft/mycroft.conf

exit 0
