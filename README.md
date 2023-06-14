# spack-config

Edits to this config should be made on your local machine, pushed here, and pulled down to Unity.

Deployment:
```sh
version="0.20.0"
mkdir /modules/spack/${version}
cd /modules/spack/${version}
# clone this repo via HTTPS, not SSH
git clone https://github.com/UMass-RC/spack-config.git .
# download and extract spack
wget https://github.com/spack/spack/releases/download/v${version}/spack-${version}.tar.gz
tar -xvf ./spack-${version}.tar.gz --strip-components=1

# deploy to production:
source /modules/spack/${VERISON}/share/spack/setup-env.sh
spack module lmod refresh -y
rm /modules/spack/latest && ln -s /modules/spack/${VERSION} /modules/spack/latest
```
