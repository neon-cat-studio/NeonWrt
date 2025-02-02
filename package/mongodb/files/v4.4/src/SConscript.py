# -*- mode: python; -*-
#
# This is the principle SConscript file, invoked by the SConstruct.  Its job is
# to delegate to any and all per-module SConscript files.

Import('env')
Import('module_sconscripts')

# NOTE: We must do third_party first as it adds methods to the environment
# that we need in the mongo sconscript
env = env.Clone()
env.SConscript('third_party/SConscript', exports=['env'])

# Inject common dependencies from third_party globally for all core mongo code
# and modules. Ideally, pcre wouldn't be here, but enough things require it
# now that it seems hopeless to remove it.
env = env.Clone()
env.InjectThirdParty(libraries=[
    'fmt',
    'safeint',
])

# Run the core mongodb SConscript.
env.SConscript('mongo/SConscript', exports=['env'])

# Run SConscripts for any modules in play
env.SConscript(module_sconscripts, exports=['env'])

