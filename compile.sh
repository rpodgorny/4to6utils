#!/bin/bash
set -e -x

export name=4to6utils
export pkgname=${name}
export pkgrel=1

git submodule update --recursive --init

./vagcompile.sh

rm -rf pkg
mkdir pkg
mkdir -p pkg/${name}
cp -av dist/* pkg/${name}/

if [ -d pkg_data ]; then
  cp -rv pkg_data/* pkg/
fi

if [ -f atxpkg_backup ]; then
  cp -av atxpkg_backup pkg/.atxpkg_backup
fi

rm -rf build dist

rm -rf package.zip
cd pkg
zip -r ../package.zip .
cd ..
rm -rf pkg

./upload.sh "$@"
