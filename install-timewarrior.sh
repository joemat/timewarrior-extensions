#!/bin/sh

which timew >/dev/null 2>&1
if [ 0 -eq $? ]
then
    echo -n "timewarrior is already installed - do you want to reinstall it? [y/N]"
    read reply
    case $reply in
    y|Y)
    ;;
    *)
        echo "aborted"
        exit 0
    esac
fi

VERSION=1.4.2

TGZ_FILE=timew-$VERSION.tar.gz

curl -L https://github.com/GothenburgBitFactory/timewarrior/releases/download/v1.4.2/$TGZ_FILE -o $TGZ_FILE

rm -rf timew-build
mkdir timew-build
cd timew-build
tar -zxvf ../$TGZ_FILE
cd timew-$VERSION
cmake -DCMAKE_BUILD_TYPE=Release .
make

sudo make install
cd ../..

## call timew in order to create configuration dirs
timew

cp flextime/flextime.py ~/.timewarrior/extensions

