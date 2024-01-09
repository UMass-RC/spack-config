# spack-config

note: while we wait for PR's to be merged and another release to come out, we are using
this fork of spack: https://github.com/simonLeary42/spack (branch releases/v0.21)

### Deployment:
```sh
version="0.21.0"
system_name="unity"
mkdir -p /modules/spack/${version}/${system_name}
cd /modules/spack/${version}/${system_name}
# clone this repo via HTTPS, not SSH
git clone https://github.com/UMass-RC/spack-config.git .
git checkout releases/${version}
# download and extract spack
cd ..
wget https://github.com/spack/spack/releases/download/v${version}/spack-${version}.tar.gz
tar -xf ./spack-${version}.tar.gz --strip-components=1
# install config files
ln -s $PWD/unity/config/* ./etc/spack/

# deploy to production:
source ./share/spack/setup-env.sh
spack module lmod refresh -y
rm /modules/spack/latest && ln -s /modules/spack/${VERSION} /modules/spack/latest
```
