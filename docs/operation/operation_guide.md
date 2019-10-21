---
id: op_opguide
title: UVAP Operation Guide
hide_title: true
---

# UVAP Operation Guide

## Introduction

This document gives a few useful topics for system integrators for operating
UVAP.

[comment]: <> (The following instructions will come here:)
[comment]: <> (## Kafka without Docker)
[comment]: <> (## Kafka cluster)
[comment]: <> (## Multi GPU usage)

## Time Synchronization Using NTP

Software components have algorithms that use the system clock. UVAP continuously
checks time, and a divergent clock response is interpreted as corrupted data.
The behavior under such circumstances is undefined.

For example, if UVAP requests the time and the system responds `T` but for
another request later, the system responds `T - 3 seconds`, a failure occurs,
such as; data loss or service error.  
Same applies if `3 seconds` passes on the clock, while in real life only
`10 milliseconds` passes.

For this reason, it is important to have the server clock accurate, monotonic
and without jumps. It is strongly recommended not to use `systemd-timesyncd`,
the default time synchronization on most systems. Use NTP or Chrony with proper
configuration that fits the requirements above.

For information on enabling NTP time synchronization using the GUI or CLI, see
_Time Synchronization using NTP_ under
<a href="https://help.ubuntu.com/community/UbuntuTime" target="_blank">UbuntuTime</a>.