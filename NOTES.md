# Cascade Intro 

Cascade is a completely classical information reconcilliation protocol.
It is like client-server where Bob is client and Alice is server (Depends on type of network. In the traditional STN network we are working with this is true. In a TN we would have the sender as server and receiver as client as EC done at every link. Similar may be considered for partially error corrected STNs?)

Consider Cascade as a blackbox algorithm with just Input and Output (Note: Bob initiates the cascade protocol)
Input would be the info Bob has i.e. Noisy Key and QBER (Estimated Quantum Bit Error Rate)
Output would be a Reconcilliated Key and Amt. of Leaked Info

It is the job of the Cascade protocol to determine which bits exactly are in error and to fix them.

Cascade does not guarantee that all bit errors are corrected. In other words, Bob’s reconciliated key is still not guaranteed to be the same as Alice’s correct key. Even after the reconciliation is complete, there is still a remaining bit error rate. The remaining bit error rate is orders of magnitude smaller than the original bit error rate before Cascade was run. But it is not zero. That is why we prefer to use the term reconciliated key and not corrected key, although it used sometimes.

Cascade does not contain any mechanism to detect and report whether the reconciliation was successful. It will neither detect nor report that there are any remaining bit errors after reconciliation. Some mechanism outside of Cascade is needed to validate whether the reconciliated key is correct or not.

Cascade can keep track of how much info was leaked. Specifically, Cascade running at Bob (Client) can keep track of which parities he asked Alice (Server) to compute. We must assume that Eve will also know about those parities. We can express the amount of leaked information in terms of leaked key bits (this is a logical abstraction - it does not indicate which specific key bits were leaked, it only provides a measure of how much information was leaked) The amount of leaked information may be used by the privacy amplification phase that runs after the information reconciliation phase to determine how much amplification is needed

# Cascade Algorithm Breakdown (Iterations)

