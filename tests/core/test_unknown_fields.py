"""Tests for unknown field warnings on KubeModel subclasses."""

import warnings

import pytest
from pydantic import ValidationError

from k8smith.core.models import (
    Container,
    ContainerPort,
    PodSecurityContext,
    SecurityContext,
    Toleration,
    TopologySpreadConstraint,
    VolumeMount,
)


def _catch_warnings(fn):
    """Run fn and return list of caught UserWarnings."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fn()
    return [w for w in caught if issubclass(w.category, UserWarning)]


class TestUnknownFieldWarnings:
    """Unknown fields should produce warnings, not silently vanish."""

    def test_toleration_typo(self):
        caught = _catch_warnings(lambda: Toleration(key="gpu", effekt="NoSchedule"))
        assert len(caught) == 1
        assert "effekt" in str(caught[0].message)
        assert "Toleration" in str(caught[0].message)

    def test_pod_security_context_typo(self):
        caught = _catch_warnings(lambda: PodSecurityContext(runAsNonRooot=True, fsGroup=1000))
        assert len(caught) == 1
        assert "runAsNonRooot" in str(caught[0].message)

    def test_security_context_wrong_level(self):
        """fsGroup is a pod-level field, not container-level."""
        caught = _catch_warnings(lambda: SecurityContext(fsGroup=1000, readOnlyRootFilesystem=True))
        assert len(caught) == 1
        assert "fsGroup" in str(caught[0].message)

    def test_volume_mount_typo(self):
        caught = _catch_warnings(
            lambda: VolumeMount(name="cfg", mountPath="/etc/cfg", sub_paths="app.conf")
        )
        assert len(caught) == 1
        assert "sub_paths" in str(caught[0].message)

    def test_container_case_typo(self):
        caught = _catch_warnings(
            lambda: Container(
                name="web",
                image="nginx",
                imagePullpolicy="Always",
                ports=[ContainerPort(containerPort=80)],
            )
        )
        assert len(caught) == 1
        assert "imagePullpolicy" in str(caught[0].message)

    def test_topology_spread_constraint_typo(self):
        """Typo on a required field: warns AND raises ValidationError."""
        with pytest.raises(ValidationError):
            _catch_warnings(
                lambda: TopologySpreadConstraint(
                    maxSkew=1,
                    topologiKey="kubernetes.io/hostname",
                    whenUnsatisfiable="ScheduleAnyway",
                )
            )

    def test_multiple_unknown_fields(self):
        caught = _catch_warnings(lambda: Toleration(kye="gpu", effekt="NoSchedule"))
        assert len(caught) == 1
        msg = str(caught[0].message)
        assert "kye" in msg
        assert "effekt" in msg

    def test_valid_fields_no_warning(self):
        """Correct usage should produce zero warnings."""
        caught = _catch_warnings(
            lambda: Toleration(
                key="gpu", operator="Exists", effect="NoSchedule", tolerationSeconds=3600
            )
        )
        assert len(caught) == 0

    def test_valid_snake_case_no_warning(self):
        """Snake_case field names should also be accepted without warning."""
        caught = _catch_warnings(lambda: PodSecurityContext(run_as_non_root=True, fs_group=1000))
        assert len(caught) == 0
