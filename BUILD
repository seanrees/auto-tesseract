load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_pkg//:pkg.bzl", "pkg_tar", "pkg_deb")

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [
        requirement("inotify"),
    ],
)

py_test(
    name = "main_test",
    srcs = ["main_test.py"],
    deps = [
        ":main",
    ],
    data = [
        "testdata/thisisasamplepdf.pdf",
    ],
)

py_test(
    name = "main_integration_test",
    srcs = ["main_integration_test.py"],
    size = 'medium',
    deps = [
        ":main",
    ],
    data = [
        "testdata/thisisasamplepdf.pdf",
    ],
)

pkg_tar(
    name = "deb-bin",
    package_dir = "/opt/auto-tesseract/bin",
    # This depends on --build_python_zip.
    srcs = [":main"],
    mode = "0755",
)

pkg_tar(
    name = "deb-default",
    package_dir = "/etc/default",
    srcs = ["debian/auto-tesseract"],
    mode = "0644",
    strip_prefix = "debian/"
)

pkg_tar(
    name = "deb-service",
    package_dir = "/lib/systemd/system",
    srcs = ["debian/auto-tesseract.service"],
    mode = "0644",
    strip_prefix = "debian/"
)

pkg_tar(
    name = "debian-data",
    deps = [
      ":deb-bin",
      ":deb-default",
      ":deb-service",
    ]
)

pkg_deb(
    name = "main-deb",
    architecture = "all",
    built_using = "bazel",
    data = ":debian-data",
    depends = [
        "python3",
        "tesseract-ocr",
        "imagemagick",
    ],
    prerm = "debian/prerm",
    description_file = "debian/description",
    maintainer = "Sean Rees <sean at erifax.org>",
    package = "auto-tesseract",
    version = "0.0.1",
)
