import React from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page">
      <div className="hero-section">
        <h1>Solana Composability Benchmark</h1>
        <p className="subtitle">
          How Well Can LLMs Build Complex Transactions?
        </p>
        <Link to="/trajectories" className="cta-button">
          Explore Trajectories →
        </Link>
      </div>

      <div className="content-section">
        <section>
          <p className="intro">
            Why can't we simply ask an LLM to write a crypto trading bot—one
            that listens to token prices, spots price differences between DEXes,
            and makes money by exploiting them? That would be amazing. The bot
            could monitor the chain, buy low on one platform, sell high on
            another, and do it all in seconds. We're not quite there yet—but
            this experiment explores how close we can get today by measuring how
            well LLMs can string together diverse Solana programs in a single
            transaction.
          </p>
        </section>

        <section>
          <h2>The Problem with Today's Blockchain Agents</h2>
          <p>
            Building superintelligent blockchain agents that respond to market
            changes is still one of the biggest challenges in the crypto
            community. Most current blockchain agents use RAG-augmented LLMs
            connected to fixed toolsets—sometimes via MCP servers—to execute
            predefined actions. They handle simple tasks fine, but break down
            when the environment changes in subtle ways.
          </p>
          <p>
            On blockchains, the same token can be priced differently across
            decentralized exchanges, lending protocols, and other on-chain
            programs. In theory, a bot could exploit those differences. In
            practice, doing so often requires chaining multiple programs
            together in the correct order—sometimes within a single
            transaction—before the opportunity disappears. Most current LLM
            agents can't plan and execute these complex, multi-step interactions
            reliably, so they miss out.
          </p>
        </section>

        <section>
          <h2>Why Solana Makes This Harder And More Interesting</h2>
          <p>
            Solana's architecture is uniquely suited for complex transactions.
            Unlike many EVM-based chains, where one transaction typically calls
            one contract, Solana allows a single transaction to invoke many
            different programs. This makes it possible to compose highly
            efficient multi-protocol operations—but it also demands more
            reasoning and composability from the agent.
          </p>
          <p>A truly capable Solana agent should be able to:</p>
          <ol>
            <li>
              <strong>Compose</strong> complex transactions spanning multiple
              programs.
            </li>
            <li>
              <strong>Debug</strong> malformed transactions using onchain
              metadata.
            </li>
            <li>
              <strong>Chain</strong> multiple transactions into coherent
              long-term strategies.
            </li>
          </ol>
          <p>
            These capabilities are exactly what's needed to profit from
            cross-program price differences at scale. They're the missing piece
            in today's LLM agents.
          </p>
        </section>

        <section>
          <h2>The Holy Grail: A True Financial Sandbox</h2>
          <p>
            In an ideal world, we could run a perfect financial test: a
            sandboxed replica of mainnet where an LLM could detect arbitrage
            opportunities and execute real transactions in response. This would
            be the holy grail of LLM blockchain agents; a proving ground for the
            next generation of AI agent engineering.
          </p>
          <p>
            Thanks to{" "}
            <a
              href="https://surfpool.run"
              target="_blank"
              rel="noopener noreferrer"
            >
              Surfpool
            </a>
            , we can already spin up sandboxed versions of mainnet and let
            agents submit transactions safely. What we can't yet do is track an
            agent's entire portfolio in that sandbox with the same accuracy and
            completeness as Jupiter Portfolio. Running a local test validator
            with full portfolio tracking is beyond the scope of this project.
          </p>
        </section>

        <section>
          <h2>Our Simplified Approach</h2>
          <p>
            Since we can't yet run the perfect arbitrage simulation, we went
            simpler: measure an LLM's ability to chain together as many unique
            Solana program instructions as possible in successful transactions.
            On Solana, instructions are the atomic building blocks of program
            interaction, and successfully chaining diverse instructions together
            signals a deeper understanding of Solana protocols.
          </p>
          <p>
            This acts as a proxy for deep Solana fluency—testing whether a model
            can compose, sequence, and execute complex multi-program
            interactions, even without a direct profit motive. If a model can't
            build diverse and valid transactions in a controlled setting, it's
            unlikely to succeed in the chaotic world of on-chain arbitrage.
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
