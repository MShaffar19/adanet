# Copyright 2019 The AdaNet Authors. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""An internal AdaNet model architecture definition."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from adanet.core import architecture_pb2 as arch_proto


class _Architecture(object):
  """An AdaNet model architecture.

  This data structure is the blueprint for reconstructing an an AdaNet model. It
  is serializable and deserializable for persistent storage.
  """

  def __init__(self):
    self._subnets = []

  @property
  def subnetworks(self):
    """The component subnetworks grouped by iteration number.

    Returns:
      An Iterable of (iteration_number, builder_name) tuples where the builder
        names are grouped by iteration number.
    """

    subnet_by_iteration = {}
    for iteration_number, builder_name in self._subnets:
      if iteration_number not in subnet_by_iteration:
        subnet_by_iteration[iteration_number] = []
      subnet_by_iteration[iteration_number].append(builder_name)
    return tuple([
        (i, tuple(subnet_by_iteration[i])) for i in sorted(subnet_by_iteration)
    ])

  def add_subnetwork(self, iteration_number, builder_name):
    """Adds the given subnetwork metadata.

    Args:
      iteration_number: Integer iteration number when this Subnetwork was
        created.
      builder_name: String name of the `adanet.subnetwork.Builder` that produced
        this Subnetwork.
    """
    self._subnets.append((iteration_number, builder_name))

  def serialize(self):
    """Returns a string serialization of this object."""

    ensemble_arch_pb = arch_proto.Ensemble()
    for iteration_number, builder_name in self._subnets:
      subnetwork_arch_pb = ensemble_arch_pb.subnetworks.add()
      subnetwork_arch_pb.iteration_number = iteration_number
      subnetwork_arch_pb.builder_name = builder_name
    return ensemble_arch_pb.SerializeToString()

  @staticmethod
  def deserialize(serialized_architecture):
    """Deserializes a serialized architecture.

    Args:
      serialized_architecture: String representation of an `_Architecture`
        obtained by calling `serialize`.

    Returns:
      A deserialized `_Architecture` instance.
    """

    ensemble_arch_pb = arch_proto.Ensemble()
    ensemble_arch_pb.ParseFromString(serialized_architecture)
    architecture = _Architecture()
    for subnet in ensemble_arch_pb.subnetworks:
      architecture.add_subnetwork(subnet.iteration_number, subnet.builder_name)
    return architecture
