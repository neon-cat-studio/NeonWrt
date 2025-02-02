# -*- mode: python -*-

import sys

Import("env")
Import("has_option")
Import("debugBuild")
Import("get_option")

env = env.Clone()

files = [
    "LIBRARY/float128/dpml_exception.c",
    "LIBRARY/float128/dpml_four_over_pi.c",
    "LIBRARY/float128/dpml_ux_bessel.c",
    "LIBRARY/float128/dpml_ux_bid.c",
    "LIBRARY/float128/dpml_ux_cbrt.c",
    "LIBRARY/float128/dpml_ux_erf.c",
    "LIBRARY/float128/dpml_ux_exp.c",
    "LIBRARY/float128/dpml_ux_int.c",
    "LIBRARY/float128/dpml_ux_inv_hyper.c",
    "LIBRARY/float128/dpml_ux_inv_trig.c",
    "LIBRARY/float128/dpml_ux_lgamma.c",
    "LIBRARY/float128/dpml_ux_log.c",
    "LIBRARY/float128/dpml_ux_mod.c",
    "LIBRARY/float128/dpml_ux_ops.c",
    "LIBRARY/float128/dpml_ux_ops_64.c",
    "LIBRARY/float128/dpml_ux_pow.c",
    "LIBRARY/float128/dpml_ux_powi.c",
    "LIBRARY/float128/dpml_ux_sqrt.c",
    "LIBRARY/float128/dpml_ux_trig.c",
    "LIBRARY/float128/sqrt_tab_t.c",
    "LIBRARY/src/bid128.c",
    "LIBRARY/src/bid128_2_str_tables.c",
    "LIBRARY/src/bid128_acos.c",
    "LIBRARY/src/bid128_acosh.c",
    "LIBRARY/src/bid128_add.c",
    "LIBRARY/src/bid128_asin.c",
    "LIBRARY/src/bid128_asinh.c",
    "LIBRARY/src/bid128_atan.c",
    "LIBRARY/src/bid128_atan2.c",
    "LIBRARY/src/bid128_atanh.c",
    "LIBRARY/src/bid128_cbrt.c",
    "LIBRARY/src/bid128_compare.c",
    "LIBRARY/src/bid128_cos.c",
    "LIBRARY/src/bid128_cosh.c",
    "LIBRARY/src/bid128_div.c",
    "LIBRARY/src/bid128_erf.c",
    "LIBRARY/src/bid128_erfc.c",
    "LIBRARY/src/bid128_exp.c",
    "LIBRARY/src/bid128_exp10.c",
    "LIBRARY/src/bid128_exp2.c",
    "LIBRARY/src/bid128_expm1.c",
    "LIBRARY/src/bid128_fdimd.c",
    "LIBRARY/src/bid128_fma.c",
    "LIBRARY/src/bid128_fmod.c",
    "LIBRARY/src/bid128_frexp.c",
    "LIBRARY/src/bid128_hypot.c",
    "LIBRARY/src/bid128_ldexp.c",
    "LIBRARY/src/bid128_lgamma.c",
    "LIBRARY/src/bid128_llrintd.c",
    "LIBRARY/src/bid128_log.c",
    "LIBRARY/src/bid128_log10.c",
    "LIBRARY/src/bid128_log1p.c",
    "LIBRARY/src/bid128_log2.c",
    "LIBRARY/src/bid128_logb.c",
    "LIBRARY/src/bid128_logbd.c",
    "LIBRARY/src/bid128_lrintd.c",
    "LIBRARY/src/bid128_lround.c",
    "LIBRARY/src/bid128_minmax.c",
    "LIBRARY/src/bid128_modf.c",
    "LIBRARY/src/bid128_mul.c",
    "LIBRARY/src/bid128_nearbyintd.c",
    "LIBRARY/src/bid128_next.c",
    "LIBRARY/src/bid128_nexttowardd.c",
    "LIBRARY/src/bid128_noncomp.c",
    "LIBRARY/src/bid128_pow.c",
    "LIBRARY/src/bid128_quantexpd.c",
    "LIBRARY/src/bid128_quantize.c",
    "LIBRARY/src/bid128_rem.c",
    "LIBRARY/src/bid128_round_integral.c",
    "LIBRARY/src/bid128_scalb.c",
    "LIBRARY/src/bid128_scalbl.c",
    "LIBRARY/src/bid128_sin.c",
    "LIBRARY/src/bid128_sinh.c",
    "LIBRARY/src/bid128_sqrt.c",
    "LIBRARY/src/bid128_string.c",
    "LIBRARY/src/bid128_tan.c",
    "LIBRARY/src/bid128_tanh.c",
    "LIBRARY/src/bid128_tgamma.c",
    "LIBRARY/src/bid128_to_int16.c",
    "LIBRARY/src/bid128_to_int32.c",
    "LIBRARY/src/bid128_to_int64.c",
    "LIBRARY/src/bid128_to_int8.c",
    "LIBRARY/src/bid128_to_uint16.c",
    "LIBRARY/src/bid128_to_uint32.c",
    "LIBRARY/src/bid128_to_uint64.c",
    "LIBRARY/src/bid128_to_uint8.c",
    "LIBRARY/src/bid32_acos.c",
    "LIBRARY/src/bid32_acosh.c",
    "LIBRARY/src/bid32_add.c",
    "LIBRARY/src/bid32_asin.c",
    "LIBRARY/src/bid32_asinh.c",
    "LIBRARY/src/bid32_atan.c",
    "LIBRARY/src/bid32_atan2.c",
    "LIBRARY/src/bid32_atanh.c",
    "LIBRARY/src/bid32_cbrt.c",
    "LIBRARY/src/bid32_compare.c",
    "LIBRARY/src/bid32_cos.c",
    "LIBRARY/src/bid32_cosh.c",
    "LIBRARY/src/bid32_div.c",
    "LIBRARY/src/bid32_erf.c",
    "LIBRARY/src/bid32_erfc.c",
    "LIBRARY/src/bid32_exp.c",
    "LIBRARY/src/bid32_exp10.c",
    "LIBRARY/src/bid32_exp2.c",
    "LIBRARY/src/bid32_expm1.c",
    "LIBRARY/src/bid32_fdimd.c",
    "LIBRARY/src/bid32_fma.c",
    "LIBRARY/src/bid32_fmod.c",
    "LIBRARY/src/bid32_frexp.c",
    "LIBRARY/src/bid32_hypot.c",
    "LIBRARY/src/bid32_ldexp.c",
    "LIBRARY/src/bid32_lgamma.c",
    "LIBRARY/src/bid32_llrintd.c",
    "LIBRARY/src/bid32_log.c",
    "LIBRARY/src/bid32_log10.c",
    "LIBRARY/src/bid32_log1p.c",
    "LIBRARY/src/bid32_log2.c",
    "LIBRARY/src/bid32_logb.c",
    "LIBRARY/src/bid32_logbd.c",
    "LIBRARY/src/bid32_lrintd.c",
    "LIBRARY/src/bid32_lround.c",
    "LIBRARY/src/bid32_minmax.c",
    "LIBRARY/src/bid32_modf.c",
    "LIBRARY/src/bid32_mul.c",
    "LIBRARY/src/bid32_nearbyintd.c",
    "LIBRARY/src/bid32_next.c",
    "LIBRARY/src/bid32_nexttowardd.c",
    "LIBRARY/src/bid32_noncomp.c",
    "LIBRARY/src/bid32_pow.c",
    "LIBRARY/src/bid32_quantexpd.c",
    "LIBRARY/src/bid32_quantize.c",
    "LIBRARY/src/bid32_rem.c",
    "LIBRARY/src/bid32_round_integral.c",
    "LIBRARY/src/bid32_scalb.c",
    "LIBRARY/src/bid32_scalbl.c",
    "LIBRARY/src/bid32_sin.c",
    "LIBRARY/src/bid32_sinh.c",
    "LIBRARY/src/bid32_sqrt.c",
    "LIBRARY/src/bid32_string.c",
    "LIBRARY/src/bid32_sub.c",
    "LIBRARY/src/bid32_tan.c",
    "LIBRARY/src/bid32_tanh.c",
    "LIBRARY/src/bid32_tgamma.c",
    "LIBRARY/src/bid32_to_bid128.c",
    "LIBRARY/src/bid32_to_bid64.c",
    "LIBRARY/src/bid32_to_int16.c",
    "LIBRARY/src/bid32_to_int32.c",
    "LIBRARY/src/bid32_to_int64.c",
    "LIBRARY/src/bid32_to_int8.c",
    "LIBRARY/src/bid32_to_uint16.c",
    "LIBRARY/src/bid32_to_uint32.c",
    "LIBRARY/src/bid32_to_uint64.c",
    "LIBRARY/src/bid32_to_uint8.c",
    "LIBRARY/src/bid64_acos.c",
    "LIBRARY/src/bid64_acosh.c",
    "LIBRARY/src/bid64_add.c",
    "LIBRARY/src/bid64_asin.c",
    "LIBRARY/src/bid64_asinh.c",
    "LIBRARY/src/bid64_atan.c",
    "LIBRARY/src/bid64_atan2.c",
    "LIBRARY/src/bid64_atanh.c",
    "LIBRARY/src/bid64_cbrt.c",
    "LIBRARY/src/bid64_compare.c",
    "LIBRARY/src/bid64_cos.c",
    "LIBRARY/src/bid64_cosh.c",
    "LIBRARY/src/bid64_div.c",
    "LIBRARY/src/bid64_erf.c",
    "LIBRARY/src/bid64_erfc.c",
    "LIBRARY/src/bid64_exp.c",
    "LIBRARY/src/bid64_exp10.c",
    "LIBRARY/src/bid64_exp2.c",
    "LIBRARY/src/bid64_expm1.c",
    "LIBRARY/src/bid64_fdimd.c",
    "LIBRARY/src/bid64_fma.c",
    "LIBRARY/src/bid64_fmod.c",
    "LIBRARY/src/bid64_frexp.c",
    "LIBRARY/src/bid64_hypot.c",
    "LIBRARY/src/bid64_ldexp.c",
    "LIBRARY/src/bid64_lgamma.c",
    "LIBRARY/src/bid64_llrintd.c",
    "LIBRARY/src/bid64_log.c",
    "LIBRARY/src/bid64_log10.c",
    "LIBRARY/src/bid64_log1p.c",
    "LIBRARY/src/bid64_log2.c",
    "LIBRARY/src/bid64_logb.c",
    "LIBRARY/src/bid64_logbd.c",
    "LIBRARY/src/bid64_lrintd.c",
    "LIBRARY/src/bid64_lround.c",
    "LIBRARY/src/bid64_minmax.c",
    "LIBRARY/src/bid64_modf.c",
    "LIBRARY/src/bid64_mul.c",
    "LIBRARY/src/bid64_nearbyintd.c",
    "LIBRARY/src/bid64_next.c",
    "LIBRARY/src/bid64_nexttowardd.c",
    "LIBRARY/src/bid64_noncomp.c",
    "LIBRARY/src/bid64_pow.c",
    "LIBRARY/src/bid64_quantexpd.c",
    "LIBRARY/src/bid64_quantize.c",
    "LIBRARY/src/bid64_rem.c",
    "LIBRARY/src/bid64_round_integral.c",
    "LIBRARY/src/bid64_scalb.c",
    "LIBRARY/src/bid64_scalbl.c",
    "LIBRARY/src/bid64_sin.c",
    "LIBRARY/src/bid64_sinh.c",
    "LIBRARY/src/bid64_sqrt.c",
    "LIBRARY/src/bid64_string.c",
    "LIBRARY/src/bid64_tan.c",
    "LIBRARY/src/bid64_tanh.c",
    "LIBRARY/src/bid64_tgamma.c",
    "LIBRARY/src/bid64_to_bid128.c",
    "LIBRARY/src/bid64_to_int16.c",
    "LIBRARY/src/bid64_to_int32.c",
    "LIBRARY/src/bid64_to_int64.c",
    "LIBRARY/src/bid64_to_int8.c",
    "LIBRARY/src/bid64_to_uint16.c",
    "LIBRARY/src/bid64_to_uint32.c",
    "LIBRARY/src/bid64_to_uint64.c",
    "LIBRARY/src/bid64_to_uint8.c",
    "LIBRARY/src/bid_binarydecimal.c",
    "LIBRARY/src/bid_convert_data.c",
    "LIBRARY/src/bid_decimal_data.c",
    "LIBRARY/src/bid_decimal_globals.c",
    "LIBRARY/src/bid_dpd.c",
    "LIBRARY/src/bid_feclearexcept.c",
    "LIBRARY/src/bid_fegetexceptflag.c",
    "LIBRARY/src/bid_feraiseexcept.c",
    "LIBRARY/src/bid_fesetexceptflag.c",
    "LIBRARY/src/bid_fetestexcept.c",
    "LIBRARY/src/bid_flag_operations.c",
    "LIBRARY/src/bid_from_int.c",
    "LIBRARY/src/bid_round.c",
    "LIBRARY/src/strtod128.c",
    "LIBRARY/src/strtod32.c",
    "LIBRARY/src/strtod64.c",
    "LIBRARY/src/wcstod128.c",
    "LIBRARY/src/wcstod32.c",
    "LIBRARY/src/wcstod64.c",
]

# Define Intel decimal128 library build variables
cpp_defines = {
    'DECIMAL_CALL_BY_REFERENCE': '0',
    'DECIMAL_GLOBAL_ROUNDING': '0',
    'DECIMAL_GLOBAL_EXCEPTION_FLAGS': '0',
    'UNCHANGED_BINARY_STATUS_FLAGS': '0',
    'USE_COMPILER_F128_TYPE': '0',
    'USE_COMPILER_F80_TYPE': '0',
    'USE_NATIVE_QUAD_TYPE': '0',
}

libs = []

def removeIfPresent(lst, item):
    try:
        lst.remove(item)
    except ValueError:
        pass

def float53_object(target, source, extra_defines=None):
    source = "LIBRARY/float128/" + source + ".c"
    obj_env = env.Clone()
    defines = (extra_defines or []) + ['T_FLOAT']
    obj_env.Append(CPPDEFINES=defines)

    obj_env.Append(CCFLAGS='-w')

    return obj_env.LibraryObject(target, source)

cpp_defines['LINUX'] = '1'
cpp_defines['linux'] = '1'
libs.append('m')

# Set Architecture Defines
processor = env['TARGET_ARCH']
# Using 32 bit
if processor == 'i386' or processor == 'emscripten':
    cpp_defines['IA32'] = '1'
    cpp_defines['ia32'] = '1'
elif processor == 'arm':
    cpp_defines['IA32'] = '1'
    cpp_defines['ia32'] = '1'
elif processor == "aarch64":
    cpp_defines['efi2'] = '1'
    cpp_defines['EFI2'] = '1'
elif processor == 'mips' or processor == 'mipsel':
    cpp_defines['IA32'] = '1'
    cpp_defines['ia32'] = '1'
elif processor == 'mips64' or processor == 'mipsel64':
    cpp_defines['efi2'] = '1'
    cpp_defines['EFI2'] = '1'
# Using 64 bit little endian
elif processor == 'x86_64' or processor == 'ppc64le':
    cpp_defines['efi2'] = '1'
    cpp_defines['EFI2'] = '1'
# Using 64 bit big endian
elif processor == 's390x':
    cpp_defines['s390x'] = '1'
    cpp_defines['BID_BIG_ENDIAN'] = '1'
else:
    assert False, "Unsupported architecture: " + processor

# Set Compiler Defines
cpp_defines['gcc'] = '1'

source_files = files

env.Append(CPPDEFINES=cpp_defines)

env.Append(CCFLAGS='-w')

env.Library(
    target='intel_decimal128',
    source=source_files,
    LIBS=libs,
    LIBDEPS_TAGS=[
        'init-no-global-side-effects',
    ]
)

if env["BUILDERS"].get("Ninja", None) is not None:
    Return()

readtest = env.Program(
    target='intel_decimal128_readtest',
    source=[
        'TESTS/readtest.c',
    ],
    LIBDEPS=[
        'intel_decimal128',
    ],
    LIBS=libs,
    AIB_COMPONENT="intel-test",
    AIB_COMPONENTS_EXTRA=[
        "unittests",
        "tests",
    ]
)

if get_option("install-mode") == "hygienic":
    readtest_input = env.AutoInstall(
        target="$PREFIX_BINDIR",
        source=["TESTS/readtest.in"],
        AIB_ROLE="runtime",
        AIB_COMPONENT="intel-test",
        AIB_COMPONENTS_EXTRA=[
            "unittests",
            "tests",
        ],
    )
else:
    readtest_input = env.Install(
        target='.',
        source=['TESTS/readtest.in'],
    )

env.Depends(readtest_input, readtest)

readtest_dict = {
    '@readtest_python_interpreter@' : sys.executable.replace('\\', r'\\'),
    '@readtest_program@' : readtest[0].name,
    '@readtest_input@' : readtest_input[0].name,
}

readtest_wrapper = env.Substfile(
    target='intel_decimal128_readtest_wrapper.py',
    source=['intel_decimal128_readtest_wrapper.py.in'],
    SUBST_DICT=readtest_dict,
)
env.Depends(readtest_wrapper, readtest_input)
if get_option("install-mode") == "hygienic":
    readtest_wrapper_install = env.AutoInstall(
        target="$PREFIX_BINDIR",
        source=readtest_wrapper,
        AIB_ROLE="runtime",
        AIB_COMPONENT="intel-test",
        AIB_COMPONENTS_EXTRA=[
            "unittests",
            "tests",
        ],
    )

if get_option("install-mode") == "hygienic":
    env.RegisterTest("$UNITTEST_LIST", readtest_wrapper_install[0])
else:
    env.RegisterUnitTest(readtest_wrapper[0])

env.AddPostAction(readtest_wrapper[0], Chmod(readtest_wrapper[0], 'oug+x'))
