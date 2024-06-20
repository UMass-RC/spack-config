-- -*- lua -*-
-- Module file created by spack (https://github.com/spack/spack) on {{ timestamp }}
--
-- {{ spec.short_spec }}
--

{% block header %}
{% if short_description %}
whatis([[Name : {{ spec.name }}]])
whatis([[Version : {{ spec.version }}]])
whatis([[Target : {{ spec.target }}]])
whatis([[Short description : {{ short_description }}]])
{% endif %}
{% if configure_options %}
whatis([[Configure options : {{ configure_options }}]])
{% endif %}

{% if long_description %}
help([[{{ long_description| textwrap(72)| join() }}]])
{% endif %}
{% endblock %}

{% block provides %}
{# Prepend the path I unlock as a provider of #}
{# services and set the families of services I provide #}
{% if has_modulepath_modifications %}
-- Services provided by the package
{% for name in provides %}
family("{{ name }}")
{% endfor %}

-- Loading this module unlocks the path below unconditionally
{% for path in unlocked_paths %}
prepend_path("MODULEPATH", "{{ path }}")
{% endfor %}

{# Try to see if missing providers have already #}
{# been loaded into the environment #}
{% if has_conditional_modifications %}
-- Try to load variables into path to see if providers are there
{% for name in missing %}
local {{ name }}_name = os.getenv("LMOD_{{ name|upper() }}_NAME")
local {{ name }}_version = os.getenv("LMOD_{{ name|upper() }}_VERSION")
{% endfor %}

-- Change MODULEPATH based on the result of the tests above
{% for condition, path in conditionally_unlocked_paths %}
if {{ condition }} then
  local t = pathJoin({{ path }})
  prepend_path("MODULEPATH", t)
end
{% endfor %}

-- Set variables to notify the provider of the new services
{% for name in provides %}
setenv("LMOD_{{ name|upper() }}_NAME", "{{ name_part }}")
setenv("LMOD_{{ name|upper() }}_VERSION", "{{ version_part }}")
{% endfor %}
{% endif %}
{% endif %}
{% endblock %}

{% block autoloads %}
{% for module in autoload %}
depends_on("{{ module }}")
{% endfor %}
{% endblock %}

{% block environment %}
{% for command_name, cmd in environment_modifications %}
{% if command_name == 'PrependPath' %}
prepend_path("{{ cmd.name }}", "{{ cmd.value }}", "{{ cmd.separator }}")
{% elif command_name == 'AppendPath' %}
append_path("{{ cmd.name }}", "{{ cmd.value }}", "{{ cmd.separator }}")
{% elif command_name == 'RemovePath' %}
remove_path("{{ cmd.name }}", "{{ cmd.value }}", "{{ cmd.separator }}")
{% elif command_name == 'SetEnv' %}
setenv("{{ cmd.name }}", "{{ cmd.value }}")
{% elif command_name == 'UnsetEnv' %}
unsetenv("{{ cmd.name }}")
{% endif %}
{% endfor %}
{% endblock %}

{% block footer %}
{# In case the module needs to be extended with custom LUA code #}
local NAME = "{{spec.name}}"
local VERSION = "{{spec.version}}"
if (mode() == "load") then
    LmodMessage("loading "..NAME.." version "..VERSION)
end
if (mode() == "unload") then
    LmodMessage("unloading "..NAME.." version "..VERSION)
end

{% if spec.name == "cuda" %}
if (mode() == "load") then
    if (posix.stat("/dev/nvidiactl") == nil) then
        LmodWarning("this is not a GPU node!")
    end
end
{% endif %}

{% if spec.name == "diamond" %}
if (mode() == "load") then
local ncbirc = '/datasets/bio/ncbi-db/.ncbirc'
local searchKey = "BLASTDB"

local function parseKeyValue(file, key)
    local result = {}
    for line in file:lines() do
        _, _, k, v = string.find(line, "(%a+)=(.+)")
        if k ~= nil then
            result[k] = v
        end
    end
    return result
end
local file = io.open(ncbirc, "r")
if file ~= nil then
    local keyValuePairs = parseKeyValue(file, searchKey)
    file:close()
    for k, v in pairs(keyValuePairs) do
        if k == searchKey then
            setenv(searchKey, v)
        end
    end
else
    LmodWarning("BLASTDB could not be set automatically")
end
end
{% endif %}

{% if spec.name == "openfoam" or spec.name == "openfoam-org" %}
if mode() == "load" then
    local userdir = pathJoin(os.getenv("HOME"), "OpenFOAM", os.getenv("USER") .. "-{{ spec.version }}")
    setenv("WM_PROJECT_USER_DIR", userdir)
    setenv("FOAM_RUN", pathJoin(userdir, "run"))
    setenv("FOAM_USER_APPBIN", pathJoin(userdir, "platforms/linux64GccDPInt32Opt/bin"))
    setenv("FOAM_USER_LIBBIN", pathJoin(userdir, "platforms/linux64GccDPInt32Opt/lib"))
    prepend_path_if_exists("LD_LIBRARY_PATH", pathJoin(userdir, "platforms/linux64GccDPInt32Opt/lib"))
    prepend_path_if_exists("PATH", pathJoin(userdir, "platforms/linux64GccDPInt32Opt/bin"))
end
{% endif %}

{% if spec.name == "apptainer" %}
if (mode() == "load") then
  local username = os.getenv("USER")
  local groups_cmd_output = capture("/usr/bin/groups")

  local potential_cache_dirs = {}
  for group in groups_cmd_output:split() do
      if group ~= nil and group ~= "" then
          table.insert(potential_cache_dirs,
              pathJoin("/work", group, ".apptainer/cache")
          )
          table.insert(potential_cache_dirs,
              pathJoin("/work", group, username, ".apptainer/cache")
          )
      end
  end

  local found_cache_dirs = {}
  for _, path in ipairs(potential_cache_dirs) do
      if isDir(path) then
          table.insert(found_cache_dirs, path)
      end
  end

  if #found_cache_dirs == 0 then
      LmodMessage("")
      LmodMessage("No apptainer cache directory found. To prevent apptainer from filling up your home directory, you can create a new directory at `/work/pi_<your_pi_name>/.apptainer/cache` and reload the module.")
  else
      setenv("APPTAINER_CACHEDIR", found_cache_dirs[1]) -- index starts at 1
      if #found_cache_dirs > 1 then
          LmodMessage("")
          LmodMessage("Multiple apptainer cache directories found:")
          for _, dir in ipairs(found_cache_dirs) do
              LmodMessage("* "..dir)
          end
          LmodMessage("chosen directory: "..found_cache_dirs[1])
          LmodMessage("you can choose another directory by setting the APPTIAINER_CACHEDIR environment variable.")
      end
  end
end
{% endif %}
{% endblock %}
