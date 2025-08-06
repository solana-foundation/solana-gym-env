import * as web3 from '@solana/web3.js';
import * as anchor from '@coral-xyz/anchor';
export async function main() {
    console.log();

    const kp = web3.Keypair.generate();
    const tx = new web3.Transaction();
    tx.add(web3.SystemProgram.transfer({
        fromPubkey: kp.publicKey,
        toPubkey: kp.publicKey,
        lamports: 100000,
    }));
    tx.feePayer = kp.publicKey; tx.partialSign(kp);
    return tx.serialize({ requireAllSignatures: false }).toString('base64');
}