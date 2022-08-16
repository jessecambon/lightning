# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from pytorch_lightning.plugins.environments.cluster_environment import ClusterEnvironment


class AzureOpenMPIEnvironment(ClusterEnvironment):
    """Environment for an OpenMPI environment on Azure.

    See Azure documentation here: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-distributed-gpu#mpi
    """

    def __init__(self, devices: int = 1) -> None:
        """devices : devices per node (same as trainer parameter)"""
        super().__init__()
        self.devices = devices

    @property
    def creates_processes_externally(self) -> bool:
        """Return True if the cluster is managed (you don't launch processes yourself)"""
        return True

    @property
    def main_address(self) -> str:
        # AZ_BATCH_MASTER_NODE should be defined when num_nodes > 1
        if "AZ_BATCH_MASTER_NODE" in os.environ:
            return os.environ.get("AZ_BATCH_MASTER_NODE").split(":")[0]
        elif "AZ_BATCHAI_MPI_MASTER_NODE" in os.environ:
            return os.environ.get("AZ_BATCHAI_MPI_MASTER_NODE")

    @property
    def main_port(self) -> int:
        # AZ_BATCH_MASTER_NODE should be defined when num_nodes > 1
        if "AZ_BATCH_MASTER_NODE" in os.environ:
            return int(os.environ.get("AZ_BATCH_MASTER_NODE").split(":")[1])
        else:
            return int(47586)  # set port to arbitrary high number

    @staticmethod
    def detect() -> bool:
        return (
            "OMPI_COMM_WORLD_SIZE" in os.environ
            and "OMPI_COMM_WORLD_LOCAL_RANK" in os.environ
            and ("AZ_BATCH_MASTER_NODE" in os.environ or "AZ_BATCHAI_MPI_MASTER_NODE" in os.environ)
        )

    def world_size(self) -> int:
        return int(os.environ.get("OMPI_COMM_WORLD_SIZE"))

    def set_world_size(self, size: int) -> None:
        pass

    def global_rank(self) -> int:
        return int(os.environ.get("OMPI_COMM_WORLD_RANK"))

    def set_global_rank(self, rank: int) -> None:
        pass

    def local_rank(self) -> int:
        return int(os.environ.get("OMPI_COMM_WORLD_LOCAL_RANK"))

    def node_rank(self) -> int:
        # this may not exist, defaulting to 0
        return int(os.environ.get("OMPI_COMM_WORLD_RANK", 0)) // int(self.devices)
