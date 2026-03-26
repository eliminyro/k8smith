"""Demo: unknown field warnings on KubeModel subclasses."""

import warnings

from k8smith.core.models import (
    Container,
    ContainerPort,
    PodSecurityContext,
    SecurityContext,
    Toleration,
    TopologySpreadConstraint,
    VolumeMount,
)


def demo(title, fn):
    """Run fn, capture and print any warnings."""
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            fn()
        except Exception as e:
            print(f"  ValidationError: {e}\n")
    for w in caught:
        print(f"  WARNING: {w.message}\n")
    if not caught:
        print("  (no warnings)\n")


# --- Typos and mistakes ---

demo(
    '1. Toleration — typo: "effekt" instead of "effect"',
    lambda: Toleration(key="gpu", effekt="NoSchedule"),
)

demo(
    '2. PodSecurityContext — typo: "runAsNonRooot"',
    lambda: PodSecurityContext(runAsNonRooot=True, fsGroup=1000),
)

demo(
    '3. SecurityContext — wrong level: "fsGroup" is pod-level, not container-level',
    lambda: SecurityContext(fsGroup=1000, readOnlyRootFilesystem=True),
)

demo(
    '4. TopologySpreadConstraint — typo: "topologiKey" (also errors: required field missing)',
    lambda: TopologySpreadConstraint(
        maxSkew=1,
        topologiKey="kubernetes.io/hostname",
        whenUnsatisfiable="ScheduleAnyway",
    ),
)

demo(
    '5. VolumeMount — typo: "sub_paths" instead of "sub_path"',
    lambda: VolumeMount(name="config", mountPath="/etc/config", sub_paths="app.conf"),
)

demo(
    '6. Container — case typo: "imagePullpolicy" (lowercase p)',
    lambda: Container(
        name="web",
        image="nginx:1.25",
        imagePullpolicy="Always",
        ports=[ContainerPort(containerPort=80)],
    ),
)

# --- Correct usage ---

demo(
    "7. Correct usage — no warnings expected",
    lambda: (
        Toleration(key="gpu", operator="Exists", effect="NoSchedule", tolerationSeconds=3600),
        PodSecurityContext(runAsNonRoot=True, fsGroup=1000),
    ),
)
