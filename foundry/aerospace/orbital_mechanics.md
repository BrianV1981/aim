# NASA Orbital Mechanics & Delta-V Fundamentals
**Source:** NASA Glenn Research Center / JPL Basics of Space Flight

## 1. Fundamental Constants
*   **Earth's Gravitational Parameter ($\mu$):** 398,600 km^3/s^2
*   **Earth's Equatorial Radius ($R_E$):** 6,378 km

## 2. Standard Orbit Altitudes
*   **Low Earth Orbit (LEO) Parking Altitude ($h_{LEO}$):** 300 km
*   **Geostationary Earth Orbit Altitude ($h_{GEO}$):** 35,786 km

*Note: To calculate the actual orbital radius ($r$), you must add the Earth's radius to the altitude.*
*   $r_1 = R_E + h_{LEO}$
*   $r_2 = R_E + h_{GEO}$

## 3. The Hohmann Transfer (Coplanar)
The most fuel-efficient two-impulse maneuver to transfer between two circular, coplanar orbits.

### Step A: Initial Circular Velocities
Calculate the velocity of the spacecraft in its initial and final circular orbits:
*   $v_{LEO} = \sqrt{\frac{\mu}{r_1}}$
*   $v_{GEO} = \sqrt{\frac{\mu}{r_2}}$

### Step B: Transfer Orbit Velocities
The transfer orbit is an ellipse intersecting both $r_1$ and $r_2$. 
The semi-major axis of the transfer ellipse is: $a_{trans} = \frac{r_1 + r_2}{2}$

Using the Vis-Viva equation ($v = \sqrt{\mu(\frac{2}{r} - \frac{1}{a})}$):
*   **Velocity at Transfer Perigee ($v_{tp}$):** $\sqrt{\mu(\frac{2}{r_1} - \frac{1}{a_{trans}})}$
*   **Velocity at Transfer Apogee ($v_{ta}$):** $\sqrt{\mu(\frac{2}{r_2} - \frac{1}{a_{trans}})}$

### Step C: Burn Delta-V Requirements
The total $\Delta v$ is the sum of the two impulsive burns required to enter and exit the transfer ellipse:
1.  **Burn 1 (LEO to Transfer Ellipse):** $\Delta v_1 = v_{tp} - v_{LEO}$
2.  **Burn 2 (Transfer Ellipse to GEO):** $\Delta v_2 = v_{GEO} - v_{ta}$

Total Coplanar Hohmann $\Delta v = \Delta v_1 + \Delta v_2$

## 4. Non-Coplanar Transfers (Inclination Change)
If launching from a non-equatorial site (e.g., Kennedy Space Center at 28.5 degrees), an inclination change ($\Delta i$) is required. This is performed most efficiently at the apogee of the transfer orbit where velocity is lowest.

The combined Burn 2 (circularization + inclination change) is calculated via the Law of Cosines:
*   $\Delta v_{combined\_burn2} = \sqrt{v_{ta}^2 + v_{GEO}^2 - 2 \cdot v_{ta} \cdot v_{GEO} \cdot \cos(\Delta i)}$

Total Non-Coplanar $\Delta v = \Delta v_1 + \Delta v_{combined\_burn2}$
