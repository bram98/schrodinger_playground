# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 00:27:45 2025

@author: bverr
"""
import numpy as np
import scipy


class Simulator:
    methods = [
        "re_im_leapfrog",
        "forward_euler",
        "find_ground_state",
        "find_ground_state_arnoldi",
    ]

    def __init__(
        self,
        N=100,
        L=1,
        psi0=None,
        potential=None,
        hbar=1.0,
        m=1.0,
        dt=0.1,
        method="re_im_leapfrog",
        potential_inf_at=100,
    ):

        self.x = np.linspace(-L / 2, L / 2, num=N, endpoint=False)
        self.dx = self.x[1] - self.x[0]
        if psi0 is None:
            self.psi = np.ones(N, dtype=complex)
        else:
            self.psi = np.asarray(psi0, dtype=complex)
        self.normalize()

        if potential is None:
            potential = np.zeros(N)
        elif hasattr(potential, "__call__"):  # potential is a function
            potential = potential(self.x)

        self.potential = np.asarray(potential)

        self.hbar = hbar
        self.m = m
        self.dt = dt
        self.method = method
        self.potential_inf_at = potential_inf_at

    def set_psi(self, psi, normalize=True):
        self.psi = np.asarray(psi, dtype=complex)
        if normalize:
            self.normalize()

    def normalize(self, inplace=True):
        norm = np.linalg.norm(self.psi) * np.sqrt(self.dx)
        # print(self.psi, norm)
        if inplace:
            self.psi /= norm

            return self.psi
        else:
            return self.psi / norm

    def hamiltonian(self, psi):
        laplacian = (np.roll(psi, 1) + np.roll(psi, -1) - 2 * psi) / (
            self.dx**2
        )
        kinetic = -self.hbar**2 / (2 * self.m) * laplacian
        potential = self.potential * psi
        self.kinetic = kinetic
        self.potential_ = potential.copy()
        # print(potential)
        return kinetic + potential

    def truncate_inf_potential(self):
        """
        This simulation considers the potential infinite when it is larger (or
        equal to) self.potential_inf_at. It will set the wavefunction to zero
        where this is the case.
        """
        inf_potential_location = np.where(
            self.potential >= self.potential_inf_at
        )
        self.psi[inf_potential_location] = 0

    def step(self):
        if self.potential_inf_at is not None:
            self.truncate_inf_potential()

        self._step()

    def forward_euler(self):
        """
        This is a "naive" forward Euler. It is unconditionally unstable.
        """

        H = self.hamiltonian(self.psi)
        self.psi = self.psi - 1j * self.dt * H
        self.normalize()

    def re_im_leapfrog(self):
        """
        https://scicomp.stackexchange.com/a/10880/26556
        """

        R, I = self.psi.real, self.psi.imag

        R_old = R.copy()
        I_old = I.copy()

        H_I = self.hamiltonian(I)
        R = R + self.dt * H_I

        H_R = self.hamiltonian(R)
        I = I - self.dt * H_R

        # norm = np.sqrt(R**2 + I * I_old)
        # self.psi /= norm

        self.psi = R + 1j * I

        self.normalize()

    def find_ground_state(self):
        H_psi = self.hamiltonian(self.psi)
        self.psi = self.psi - self.dt * H_psi
        # self.psi = self.psi - H_psi
        self.normalize()

    def find_ground_state_arnoldi(self):
        """
        Gemini made this. The idea behind arnoldi iteration is to use multiple
        iterations of Hpsi, H^2psi, H^3psi etc.
        """
        norm_old = np.linalg.norm(self.psi)
        q1 = self.psi / norm_old

        # 2. Apply Hamiltonian (Generate the Krylov subspace)
        # We want the subspace span{q1, H*q1}
        H_q1 = self.hamiltonian(q1)

        h11 = np.vdot(q1, H_q1).real

        residual = H_q1 - h11 * q1

        h12 = np.linalg.norm(residual)

        # Safety check: If residual is 0, we are at the exact eigenstate
        if np.abs(h12) < 1e-10:
            self.psi = q1  # Keep old state
            self.normalize()
            return

        # q2 is the normalized residual
        q2 = residual / h12

        H_q2 = self.hamiltonian(q2)

        h22 = np.vdot(q2, H_q2).real

        # Note: Because H is Hermitian, the matrix is tridiagonal.
        # The off-diagonal element <q1|H|q2> is exactly the norm h12 we calculated!
        # We construct the 2x2 matrix T:
        # [ h11  h12 ]
        # [ h12  h22 ]
        H_sub = np.array([[h11, h12], [h12, h22]])

        evals, evecs = np.linalg.eigh(H_sub)

        c1, c2 = evecs[:, 0]
        c_norm = np.sqrt(c1**2 + c2**2)
        self.psi = c1 * q1 + c2 * q2

        # No need to normalize here explicitly as c1^2 + c2^2 = 1
        # and q1, q2 are orthonormal, but good for safety.
        self.normalize()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, _method):
        self._method = _method
        self._step = getattr(self, _method)
