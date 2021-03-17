#!/bin/bash
set -e -x

export name=4to6utils
export pkgname=${name}
export pkgrel=1

test -f package.zip

if [ "$1" == "" ]; then
  export datetime=`gawk "BEGIN {print strftime(\"%Y%m%d%H%M%S\")}"`
  echo "devel version $datetime"
  #export branch=`git rev-parse --abbrev-ref HEAD`
  #export pkgname=${pkgname}.dev.${branch}
  export pkgname=${pkgname}.dev
  export version=$datetime
  export upload=atxpkg@atxpkg-dev.asterix.cz:atxpkg/
elif [ "$1" == "release" ]; then
  export version=`git describe --tags --abbrev=0`
  export version=${version:1}
  echo "release version $version"
  export upload=atxpkg@atxpkg.asterix.cz:atxpkg/
else
  echo "unknown parameter!"
  exit
fi

export pkg_fn=${pkgname}-${version}-${pkgrel}.atxpkg.zip

mv package.zip $pkg_fn

rsync -avP $pkg_fn $upload

echo "DONE: ${pkg_fn}"
