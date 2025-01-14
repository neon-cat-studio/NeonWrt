# -*- mode: python; -*-
Import("env")

env = env.Clone()

def removeIfPresent(lst, item):
    try:
        lst.remove(item)
    except ValueError:
        pass

for to_remove in ['-Werror', "-Wsign-compare","-Wall","-Werror=unused-result"]:
    removeIfPresent(env['CCFLAGS'], to_remove)
    removeIfPresent(env['CFLAGS'], to_remove)

env.Append(CPPDEFINES=['KMS_MSG_STATIC'])

additional_sources = []

additional_sources.append(['src/kms_crypto_openssl.c'])

env.Library(
    target="kms-message",
    source=[
        'src/hexlify.c',
        'src/kms_b64.c',
        'src/kms_caller_identity_request.c',
        'src/kms_decrypt_request.c',
        'src/kms_encrypt_request.c',
        'src/kms_kv_list.c',
        'src/kms_message.c',
        'src/kms_request.c',
        'src/kms_request_opt.c',
        'src/kms_request_str.c',
        'src/kms_response.c',
        'src/kms_response_parser.c',
        'src/sort.c',
    ] + additional_sources,
    LIBDEPS_TAGS=[
        'init-no-global-side-effects',
    ],
)
