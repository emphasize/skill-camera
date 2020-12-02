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

dependencies=( python-opencv )

# default pm
pm="sudo apt-get install -y"

#setting dependencies and package manager in relation to the distribution
if os_is_like arch || os_is arch; then
    pm="sudo pacman -Sy --needed"
elif os_is_like debian || os_is debian || os_is_like ubuntu || os_is ubuntu || os_is linuxmint || os_is antiX; then
    pm="sudo apt-get install -y"
elif found_exe pkcon; then
    pm="pkcon install"
elif os_is_like fedora || os_is fedora || os_is rhel || os_is centos; then
    dependencies=( opencv-python)
    pm="sudo yum -y install"
fi


# installing dependencies
for dep in "${dependencies[@]}"
do
    echo "installing: $dep"
    $pm $dep
done

exit 0
