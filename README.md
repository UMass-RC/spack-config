# spack-config

note: while we wait for PR's to be merged and another release to come out, we are using
this fork of spack: https://github.com/simonLeary42/spack (branch releases/v0.21)

### Deployment:
```sh
version="0.21"
system_name="unity"

# git clone
mkdir  /modules/spack/${version}
cd /modules/spack/${version}
git clone https://github.com/spack/spack.git .
git checkout releases/v${version}
mkdir ${system_name}
cd ${system_name}
git clone https://github.com/UMass-RC/spack-config.git .
git checkout releases/v${version}

# install config files
ln -s /modules/spack/${version}/unity/config/* ./etc/spack/

# deploy to production
source ./share/spack/setup-env.sh
spack module lmod refresh -y
rm /modules/spack/latest && ln -s /modules/spack/${VERSION} /modules/spack/latest
cd /modules/spack/${version}/${system_name}
./update-spider-cache.sh
```
