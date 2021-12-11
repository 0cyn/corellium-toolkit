# corellium-toolkit 

some various tools, etc i use for working with corellium

## Installing/Updating

`python3 -m pip install --force-reinstall git+git://github.com/KritantaDev/corellium-toolkit`

## Tools

`cachebuilder` - Automatically grabs a list of devices connected over USB (including USBFlux), and allows you to set up the XCode cache for them.

Using this tool keeps XCode from needing to download the 2GB file over USB (or even slower, USBFlux).

run `cachebuilder` in terminal after installation to use

WIP:

`corctl` is a Shell-styled interface for interacting with the Corellium Web API, controlling devices/projects, etc. 

`src/kcorellium` is a python based API Wrapper for Corellium's web api

---

i am not officially associated with corellium inc. this project has not been endorsed by them. the corellium web API is not
publicly documented, is not publicly supported, and is liable to change at any time without notice. 
