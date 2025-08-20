import React from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page">
      <div className="hero-section">
        <h1>Solana Bench</h1>
        <p className="subtitle">
          How Well Can LLMs Build Complex Transactions?
        </p>
        <Link to="/trajectories" className="cta-button">
          Explore Trajectories →
        </Link>
      </div>

      <div className="content-section">
        <section>
          <h2>Introduction</h2>
          <p className="intro">
            LLMs are getting better at writing code on demand, but how well can
            they use this code to operate on Solana's runtime? Instead of asking
            language models to run profitable Defi strategies (which requires
            complex read infrastructure), we introduce two qualitative
            benchmarks environments that directly test a model's protocol
            fluency and compositional reasoning on Solana:
            <ol>
              <li>
                <b>Basic</b> - maximize the number of <b>new instructions</b>{" "}
                successfully executed using only foundational SDKs (e.g.
                @solana/web3.js, Anchor, etc)
              </li>
              <li>
                <b>Swap</b> - same success criterion, but within a Defi-leaning
                surface (Jupiter, Orca, Raydium, Phoenix, Meteora) via
                additional example prompts and preinstalled SDKs
              </li>
            </ol>
            These environments are not about measuring profit and loss. They are
            about <b>operational Solana competence</b>: composing valid
            transactions, choosing accounts appropriately, using SDKs correctly,
            recovering from errors, and exploring breadth across programs.
          </p>
        </section>

        <section>
          <h2>Why a qualitative benchmark (and not a trading benchmark)?</h2>
          <p>
            Modeling trading strategies require a high-fidelity market harness
            (stateful price feeds, slippage & MEV modeling, portfolio indexing,
            latency models, etc). This is a full product, with constantly moving
            goalposts due to how fast Solana market structure evolves. By
            contrast, Solana Bench environments are (1) <b>objective</b>, (2)
            <b>reproducible</b>, and (3) <b>diagnostic</b>: you can see exactly
            which programs and instruction variants a model can compose and
            where it fails.
          </p>
        </section>

        <section>
          <h2>Evaluation Protocol</h2>
          <p>
            <ol>
              <li>
                <b>Budget</b>: 50 messages per model per run
              </li>
              <li>
                <b>Per-turn constraint</b>: Model emits <b>Typescript</b> that
                must produce <b>exactly one unsigned transaction</b> that will
                be signed by the environment
              </li>
              <li>
                <b>Execution</b>: Run against a sandboxed Solana validator (
                <a
                  href="https://surfpool.run"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Surfpool
                </a>
                ) that mimics mainnet
              </li>
              <li>
                <b>Reward</b>: # of unique instructions from successfully
                executed transactions
              </li>
            </ol>
          </p>
        </section>

        <section>
          <h2>Call to Action</h2>
          <p>
            Expand on this research! We're funding up to $5k for open-sourced
            research on high-quality Solana benchmarks. Here are some ideas:
            <ol>
              <li>
                <b>Protocol Environments</b>: setup environment where LMs are
                only rewarded for interacting with a specific protocol. This
                could be good to understand which Defi protocols are LMs best at
                using & why?
              </li>
              <li>
                <b>DevEx Environments</b>: setup environment where LMs only have
                access to IDLs, or IDL-generated methods instead of SDKs. This
                could be used to improve IDL tooling.
              </li>
              <li>
                <b>System Prompts Improvements</b>: LMs are very sensitive to
                system prompts. We are open to clear improvements to the system
                prompts, so long as the changes are well explained and result in
                meaningful changes in benchmark performance.
              </li>
              <li>
                <b>Evaluating custom models</b>: we welcome evaluations of
                custom Solana models, but humbly request that the evaluation
                methodology be included, with some way for us to reproduce the
                results.
              </li>
            </ol>
            Apply for funding{" "}
            <a
              href="https://share.hsforms.com/1GE1hYdApQGaDiCgaiWMXHA5lohw"
              target="_blank"
              rel="noopener noreferrer"
              style={{ textDecoration: "underline" }}
            >
              here
            </a>
            .
          </p>
        </section>

        <section>
          <h2>Introducing the Solana Composability Benchmark</h2>
          <p>
            In this benchmark, each model had 50 messages to work with. In each
            message, the model could write TypeScript code to generate exactly
            one transaction. If the transaction succeeded, each unique
            instruction within it counted toward the model's total score. The
            goal: maximize the diversity of instructions within the message
            limit.
          </p>

          <div className="image-gallery">
            <img
              src="/solana-gym-env/assets/basic_reward_progression.png"
              alt="Reward Progression (Basic)"
            />
            <img
              src="/solana-gym-env/assets/swap_reward_progression.png"
              alt="Reward Progression (Defi)"
            />
            <img
              src="/solana-gym-env/assets/basic_individual_trajectories.png"
              alt="Individual Model Trajectories (Basic)"
            />
            <img
              src="/solana-gym-env/assets/swap_individual_trajectories.png"
              alt="Individual Model Trajectories (Defi)"
            />
          </div>
        </section>

        <section>
          <h2>Results</h2>
          <p>
            The results were clear: Anthropic's Claude Sonnet 4 outperformed all
            other models in discovering new programs, exploiting the reward
            environment, and composing complex Solana transactions. However, its
            high cost makes it impractical for large-scale deployment.
          </p>
          <p>
            For a more budget-friendly option, Google's Gemini 2.5 Flash proved
            the best at the lower price tier—coming close to its Pro sibling in
            raw capability while being significantly cheaper.
          </p>
        </section>

        <section className="explore-section">
          <h2>Explore the Data</h2>
          <p>
            Dive into the detailed trajectories to see how each model performed,
            what code they generated, and how they discovered new programs over
            time.
          </p>
          <Link to="/trajectories" className="cta-button">
            Explore Trajectories →
          </Link>
        </section>
      </div>
    </div>
  );
};

export default LandingPage;
