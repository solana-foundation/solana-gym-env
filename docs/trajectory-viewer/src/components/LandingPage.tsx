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
          <h2>Introducing 2 Solana Bench Environments</h2>
          <p className="intro">
            At the Solana Foundation, we want to fund open-source AI tooling
            that measurably improves how developers and applications use Solana.
            The challenge is <b>measurement</b>. Until now, we haven't had a
            simple, reproducible way to evaluate whether new tools actually make
            it easier for language models to build and run transactions on
            Solana. We've experimented with Q&A benchmarks (too costly to
            maintain), tool-calling benchmarks in agent kits (too brittle and
            fragmented across stacks), and funding one-off toolkits (hard to
            track impact). Each attempt has taught us something, but none have
            given us a sustainable standard. That's why we're introducing{" "}
            <b>Solana Bench</b> — two lightweight, open-ended environments
            designed to test LLMs' operational competence on Solana in a way
            that is <b>simple, reproducible, and objective</b>.
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
            recovering from errors, and exploring breadth across programs. They
            are inspired by qualitative benchmarks like{" "}
            <a
              href="https://www.anthropic.com/news/visible-extended-thinking"
              target="_blank"
              rel="noopener noreferrer"
            >
              ClaudePlaysPokemon
            </a>
            ,{" "}
            <a
              href="https://huggingface.co/blog/textquests"
              target="_blank"
              rel="noopener noreferrer"
            >
              TextQuest
            </a>
            {", "}
            and Nvidia's{" "}
            <a
              href="https://voyager.minedojo.org/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Voyager.
            </a>
          </p>
        </section>

        <section>
          <h2>Why Measurement Has Been Hard</h2>
          <p>
            The Solana Foundation wants to fund exceptional open-source
            development at the frontier of AI and Solana. The Foundation
            believes it has the duty to use funds responsibly and to be learn
            from past experiences. Over the last 9 months of 2025, we have
            sought & funded various efforts to evaluate LLMs on their
            operational Solana knowlege. The following are some of the things we
            have tried, and what we learned.
          </p>

          <h3 style={{ marginBottom: "10px" }}>
            What we tried — and why it wasn't sustainable
          </h3>
          <ul style={{ marginLeft: "15px", marginBottom: "20px" }}>
            <li style={{ marginBottom: "0.5rem" }}>
              <b>Q&amp;A benchmarks:</b> High-quality question-answer datasets
              take significant ongoing curation to stay accurate as programs,
              SDKs, and best practices evolve. Those hours come from the same
              teams building protocol infrastructure — a tradeoff we can't
              justify long-term. We're grateful to{" "}
              <a
                href="https://x.com/LumoLabsDotAI"
                target="_blank"
                rel="noopener noreferrer"
              >
                @LumoLabsDotAI
              </a>{" "}
              for assembling sample datasets that helped us visualize strengths
              and gaps, and to articulate the pros/cons more clearly.
            </li>
            <li style={{ marginBottom: "0.5rem" }}>
              <b>Tool-calling benchmarks in agent kits:</b> We funded the
              addition of{" "}
              <a
                href="https://github.com/sendaifun/solana-agent-kit/pull/331"
                target="_blank"
                rel="noopener noreferrer"
              >
                hundreds
              </a>{" "}
              of{" "}
              <a
                href="https://github.com/sendaifun/solana-agent-kit/pull/347"
                target="_blank"
                rel="noopener noreferrer"
              >
                tool-calling benchmarks
              </a>{" "}
              in SendAI's{" "}
              <a
                href="https://github.com/sendaifun/solana-agent-kit"
                target="_blank"
                rel="noopener noreferrer"
              >
                Solana Agent Kit
              </a>
              . The goal was to create a suite of evaluations that could be used
              to test LLM applications for regressions in their Solana
              capability before they went into production.{" "}
              <b>
                We failed at building a tool-calling benchmark useful for
                applications, but succeeded in{" "}
                <a
                  href="https://github.com/sendaifun/solana-agent-kit/pull/345"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  improving
                </a>{" "}
                Solana Agent Kit.
              </b>{" "}
              Tool-calling benchmarks measure complex and confounding behaviors:
              tool selection amonst hundreds of tools, sequential tool-calling
              to achieve complicated tasks, and recovery from failure due to
              implementation errors. Tool-calling benchmarks are useful for
              improving an LLMs usage of single toolkit, but not for a wider
              ecosystem of applications built on diverse tooling. For example,
              many Solana AI teams use ElizaOS, and are unable to use the Solana
              Agent Kit evals. We would have loved to share results with ElizaOS
              agents, since we found that many ElizaOS agents are so strongly
              guided by their character files that they will fail basic single
              tool call evaluations. But alas, the tool-calling benchmarks were
              specific to Solana Agent Kit.{" "}
            </li>
            <li style={{ marginBottom: "0.5rem" }}>
              <b>Fund more toolkits:</b> Funding more toolkits often means
              funding individual teams — not necessarily ecosystem-level
              improvements. What we were missing was a <i>simple, open-ended</i>{" "}
              benchmark that any team could run, which would let us measure
              whether our investments are actually moving AI usability forward
              on Solana.
            </li>
          </ul>

          <h3 style={{ marginBottom: "10px" }}>Why these two environments</h3>
          <p>
            The <b>Basic</b> and <b>Swap</b> environments aim to give us
            lightweight, reproducible tests of{" "}
            <b>operational Solana competence</b>. They avoid subjective P&amp;L,
            minimize ongoing maintenance, and reflect the real skill we want
            agents to demonstrate — composing valid transactions, wiring
            accounts correctly, using SDKs responsibly, recovering from errors,
            and exploring breadth across programs. We see this as a practical
            baseline for the community to iterate on together.
          </p>
        </section>

        <section>
          <h2>Evaluation Protocol</h2>
          <ol>
            <li>
              <b>Budget</b>: 50 messages per model per run
            </li>
            <li>
              <b>Per-turn constraint</b>: Model emits <b>Typescript</b> that
              must produce <b>exactly one unsigned transaction</b> that will be
              signed by the environment
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
              <b>Score</b>: # of unique instructions from successfully executed
              transactions over a single run
            </li>
          </ol>
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
                <th>Median Programs Used</th>
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
                <th>Median Programs Used</th>
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
            each model's performance.
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
          <h2>Help us help you build the future of AI on Solana</h2>
          <p>
            If you notice things we missed, or have ideas for how to improve the
            benchmarks, please let us know! We are open to funding more open
            source AI development, but need your help to measure impact. Feel
            free to reach out to us at{" "}
            <a href="mailto:ai@solana.org">ai@solana.org</a>
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
