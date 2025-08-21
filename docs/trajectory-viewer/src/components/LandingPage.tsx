import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";

const LandingPage: React.FC = () => {
  const [expandedImage, setExpandedImage] = useState<string | null>(null);

  const handleImageClick = (src: string) => {
    setExpandedImage(src);
  };

  const handleCloseModal = () => {
    setExpandedImage(null);
  };

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
          <h2>Introducing the Solana Bench Environments</h2>
          <p className="intro">
            LLMs are getting better at writing code, but how well can they use
            this code to operate on Solana's runtime? Instead of asking language
            models to run profitable Defi strategies (which requires complex
            read infrastructure and subjective performance metrics), we
            introduce two qualitative benchmarks environments that directly test
            a model's protocol fluency and compositional reasoning on Solana:
            <ol>
              <li>
                <b>Basic</b> - maximize the number of <b>new instructions</b>{" "}
                successfully executed using only foundational SDKs (e.g.
                @solana/web3.js, Anchor, etc)
              </li>
              <li>
                <b>Swap</b> - same success criterion, but within a Defi-leaning
                surface (Jupiter, Orca, Raydium, Phoenix, Meteora) using
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
            goalposts due to how fast Solana market structure evolves, not to
            mention subjective metrics with a high degree of variance (return,
            alpha, hit ratio, sharpe, etc). By contrast, Solana Bench
            environments are (1) <b>simple</b>, (2) <b>reproducible</b>, and (3){" "}
            <b>diagnostic</b>. You can see exactly which programs and
            instruction variants a model can compose and where it fails.
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
                <b>Score</b>: # of unique instructions from successfully
                executed transactions over a single run
              </li>
            </ol>
          </p>
        </section>

        <section>
          <h2>Results</h2>
          <p>
            We evaluated 4 models on each benchmark over 5 runs. We note that
            the cost for this suite of evaluations hovers around $150-200 USD at
            the time of this writing. The primary cost driver is Claude Sonnet
            4, which is roughly 10x more expensive than Gemini 2.5 Flash &
            gpt-oss-120b.
          </p>
          <h3>Basic Benchmark</h3>
          <table className="trajectory-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Median Score</th>
                <th>Max Score</th>
                <th>Min Score</th>
                <th>Median # of Programs Used</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="model-name">claude-sonnet-4</td>
                <td className="metric-value reward-high">115</td>
                <td className="metric-value">181</td>
                <td className="metric-value">30</td>
                <td className="metric-value">5</td>
              </tr>
              <tr>
                <td className="model-name">gpt-5</td>
                <td className="metric-value reward-med">60</td>
                <td className="metric-value">66</td>
                <td className="metric-value">57</td>
                <td className="metric-value">8</td>
              </tr>
              <tr>
                <td className="model-name">gemini-2.5-flash</td>
                <td className="metric-value reward-low">40</td>
                <td className="metric-value">44</td>
                <td className="metric-value">23</td>
                <td className="metric-value">6</td>
              </tr>
              <tr>
                <td className="model-name">gpt-oss-120b</td>
                <td className="metric-value reward-low">23</td>
                <td className="metric-value">25</td>
                <td className="metric-value">16</td>
                <td className="metric-value">6</td>
              </tr>
            </tbody>
          </table>
          <div className="image-gallery">
            <img
              src="/solana-gym-env/assets/basic_individual_trajectories.png"
              alt="Individual Model Trajectories (Basic)"
              onClick={() =>
                handleImageClick(
                  "/solana-gym-env/assets/basic_individual_trajectories.png"
                )
              }
              style={{ cursor: "pointer" }}
            />
          </div>
          <p>
            Claude is definitely the best performer here. Its key insight is
            that the memo programs can be used to score high without actually
            making progress on the requested task - performing swaps on DEXes.
            Beyond other models, Claude has a strong propensity to game any
            metric or task given to it. This is useful to know when dealing with
            complex environments like Solana.
          </p>

          <h3>Swap Benchmark</h3>
          <table className="trajectory-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Median Score</th>
                <th>Max Score</th>
                <th>Min Score</th>
                <th>Median # of Programs Used</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="model-name">claude-sonnet-4</td>
                <td className="metric-value reward-high">33</td>
                <td className="metric-value">102</td>
                <td className="metric-value">19</td>
                <td className="metric-value">6</td>
              </tr>
              <tr>
                <td className="model-name">gpt-5</td>
                <td className="metric-value reward-med">30</td>
                <td className="metric-value">34</td>
                <td className="metric-value">27</td>
                <td className="metric-value">16</td>
              </tr>
              <tr>
                <td className="model-name">gemini-2.5-flash</td>
                <td className="metric-value reward-low">14</td>
                <td className="metric-value">18</td>
                <td className="metric-value">0</td>
                <td className="metric-value">3</td>
              </tr>
              <tr>
                <td className="model-name">gpt-oss-120b</td>
                <td className="metric-value reward-low">10</td>
                <td className="metric-value">22</td>
                <td className="metric-value">8</td>
                <td className="metric-value">4</td>
              </tr>
            </tbody>
          </table>
          <div className="image-gallery">
            <img
              src="/solana-gym-env/assets/swap_individual_trajectories_raw.png"
              alt="Individual Model Trajectories Raw(Defi)"
              onClick={() =>
                handleImageClick(
                  "/solana-gym-env/assets/swap_individual_trajectories_raw.png"
                )
              }
              style={{ cursor: "pointer" }}
            />
          </div>
          <p>
            Claude outperforms GPT-5 slightly here, only due to one run where it
            achieved 102 rewards. This is good cause for us to investigate
            further - as noted by{" "}
            <a href="https://x.com/oceanicursula">@oceanicursula</a>{" "}
            <a
              href="https://x.com/oceanicursula/status/1956542070539386930"
              target="_blank"
              rel="noopener noreferrer"
            >
              here.
            </a>{" "}
            In this scenario, LMs are prompted to construct swap transactions
            across different DEXes. SDKs to Jupiter, Orca, Meteora, Raydium, and
            Phoenix are provided. But the LMs end up only using the Jupiter SDK
            to maximize their score.
            <br />
            <br />
            Upon further investigation, we found that Claude had found a
            loophole, and it had reward-hacked the environment by sending memo
            instructions with slightly different instruction data. After
            filtering out the Memo instructions, we got a clearer picture of
            each models' performance.
          </p>
          <h4>Filtered Swap Benchmark Performance</h4>
          <div className="image-gallery">
            <img
              src="/solana-gym-env/assets/swap_individual_trajectories.png"
              alt="Individual Model Trajectories (Defi)"
              onClick={() =>
                handleImageClick(
                  "/solana-gym-env/assets/swap_individual_trajectories.png"
                )
              }
              style={{ cursor: "pointer" }}
            />
          </div>
          <p>
            GPT-5 outperforms Claude when filtering out Memo & Memo v1 program
            instructions! This points to the difficulty in constructing
            effective and non-gameable environments. We encourage the community
            to build more well rounded environments that are not trivial to
            exploit.
            <br />
            <br />
            We also encourage the Defi community to spend a little more time
            writing great documentation & canonical swap examples using their
            SDKs. Language models are trained on public data and examples. The
            next wave of vibe coders are most likely to use whatever DEX their
            LM knows how to use.
          </p>
        </section>
        <section>
          <h2>Takeaways</h2>
          <h3>For app builders</h3>
          <p>
            We encourage app developers to put SDK examples on their
            documentation sites, or other crawler-accessible places. This will
            not result in an immediate change in LLM usability, but it will
            result improved LLM understanding of your protocol in the next wave
            of model releases. LLM-readiness can be a part of every team's
            developer adoption strategy.
          </p>
          <h3>For Developers</h3>
          <p>
            For teams that really want to go the extra mile, we recommend them
            to host APIs that abstract away the compositional logic for using
            their protocol. This includes instructions for wrapping & unwrapping
            sol, creating ATAs, setting compute budget limits, and doing other
            protocol-specific initialization steps. We notice that LLMs seem to
            really understand Jupiter's API, and are able to use it to perform
            swaps, and are basically unable to use any other DEX SDK natively.
          </p>
        </section>
        <section>
          <h2>Grant Opportunities</h2>
          <p>
            Expand on this research! We're funding up to $5k for open-sourced
            research on high-quality Solana benchmarks. Here are some ideas:
            <ol>
              <li>
                <b>Protocol Environments</b>: setup environment where LMs are
                only rewarded for interacting with a specific protocol. This
                could be good to understand which Defi protocols LMs are best at
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
                custom Solana models, but request that the evaluation
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

      {/* Image Modal */}
      {expandedImage && (
        <div
          className="image-modal-overlay"
          onClick={handleCloseModal}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.9)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            cursor: "pointer",
          }}
        >
          <img
            src={expandedImage}
            alt="Expanded view"
            style={{
              maxWidth: "90vw",
              maxHeight: "90vh",
              objectFit: "contain",
            }}
            onClick={(e) => e.stopPropagation()}
          />
          <button
            onClick={handleCloseModal}
            style={{
              position: "absolute",
              top: "20px",
              right: "20px",
              background: "white",
              border: "none",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              fontSize: "24px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
            }}
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
