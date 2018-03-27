echo if this fails
echo Open up your /etc/dphys-swapfile  file and then edit the CONF_SWAPSIZE  variable
echo
echo # set size to absolute value, leaving empty (default) then uses computed value
echo #   you most likely don't want this, unless you have an special disk situation
echo # CONF_SWAPSIZE=100
echo CONF_SWAPSIZE=1024
echo
echo sudo /etc/init.d/dphys-swapfile stop
echo sudo /etc/init.d/dphys-swapfile start
echo
echo and retry

#sudo cp /etc/dphys-swapfile /etc/dphys-swapfile.backup

sudo apt-get purge wolfram-engine
sudo apt-get purge libreoffice*
sudo apt-get clean
sudo apt-get autoremove
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install -y build-essential cmake pkg-config libjpeg-dev \
libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev \
libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev \
libgtk-3-dev libcanberra-gtk* libatlas-base-dev gfortran python2.7-dev \
python3-dev

wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.3.0.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.3.0.zip
unzip opencv_contrib.zip
sudo pip install numpy
cd ./opencv-3.3.0/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=./opencv_contrib-3.3.0/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..
make -j2
sudo make install
sudo ldconfig