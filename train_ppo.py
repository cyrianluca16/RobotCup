"""
train_ppo.py — Entraînement PPO avec Stable Baselines 3
Self-play : l'ennemi est une ancienne version de l'agent allié.

Usage :
    python train_ppo.py              # entraîner
    python train_ppo.py --test       # tester le modèle sauvegardé
"""

import argparse
import os
import json
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import (
    EvalCallback, CheckpointCallback, BaseCallback
)
from match_env import MatchEnv, GARDE_MANGERS, NID_ALLIE

# ── Configuration ─────────────────────────────────────────────
MODEL_PATH      = "modeles/ppo_eurobot"
BEST_MODEL_PATH = "modeles/best_model"
LOG_PATH        = "logs/"
N_ENVS          = 4        # environnements parallèles
TOTAL_STEPS     = 500_000  # steps d'entraînement total
EVAL_FREQ       = 10_000   # évaluation toutes les N steps
N_EVAL_EPISODES = 20       # épisodes par évaluation


# ── Callback pour afficher la progression ────────────────────
class ProgressCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_scores  = []

    def _on_step(self):
        # Récupérer les infos des épisodes terminés
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self.episode_rewards.append(info["episode"]["r"])
                if len(self.episode_rewards) % 100 == 0:
                    mean_r = np.mean(self.episode_rewards[-100:])
                    print(f"  Step {self.num_timesteps:>8} | "
                          f"Episodes {len(self.episode_rewards):>5} | "
                          f"Reward moyen (100 ep): {mean_r:+.2f}")
        return True


# ── Entraînement ─────────────────────────────────────────────
def entrainer():
    os.makedirs("modeles", exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)

    print("=" * 55)
    print("  Entraînement PPO — Eurobot 2026")
    print(f"  {N_ENVS} envs parallèles | {TOTAL_STEPS:,} steps total")
    print("=" * 55)

    # Créer les environnements vectorisés
    env = make_vec_env(MatchEnv, n_envs=N_ENVS)

    # Environnement d'évaluation séparé
    eval_env = make_vec_env(MatchEnv, n_envs=1)

    # Modèle PPO
    # Réseau léger : [64, 64] → tourne sur Raspberry Pi 4 en <2ms
    model = PPO(
        policy        = "MlpPolicy",
        env           = env,
        learning_rate = 3e-4,
        n_steps       = 512,        # steps avant mise à jour
        batch_size    = 64,
        n_epochs      = 10,
        gamma         = 0.99,       # facteur d'actualisation
        gae_lambda    = 0.95,
        clip_range    = 0.2,
        ent_coef      = 0.01,       # encourage l'exploration
        policy_kwargs = dict(
            net_arch = [64, 64]     # deux couches de 64 neurones
        ),
        verbose       = 0,
        tensorboard_log = LOG_PATH,
    )

    # Callbacks
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path = BEST_MODEL_PATH,
        log_path             = LOG_PATH,
        eval_freq            = EVAL_FREQ // N_ENVS,
        n_eval_episodes      = N_EVAL_EPISODES,
        deterministic        = True,
        verbose              = 1,
    )
    checkpoint_cb = CheckpointCallback(
        save_freq   = 50_000 // N_ENVS,
        save_path   = "modeles/checkpoints/",
        name_prefix = "ppo_eurobot",
        verbose     = 1,
    )
    progress_cb = ProgressCallback()

    # Lancer l'entraînement
    print("\nDémarrage de l'entraînement…")
    model.learn(
        total_timesteps = TOTAL_STEPS,
        callback        = [eval_cb, checkpoint_cb, progress_cb],
        progress_bar    = True,
    )

    # Sauvegarder le modèle final
    model.save(MODEL_PATH)
    print(f"\n✅ Modèle sauvegardé : {MODEL_PATH}.zip")

    # Exporter la politique en JSON pour la Raspberry
    exporter_politique_json(model)

    env.close()
    eval_env.close()


# ── Export JSON pour Raspberry Pi ────────────────────────────
def exporter_politique_json(model):
    """
    Exporte les poids du réseau en JSON.
    Sur Raspberry : charger le JSON et faire une inférence manuelle
    (2 couches Dense de 64 neurones, activation tanh).
    Taille typique : ~50 Ko.
    """
    params = {}
    for name, param in model.policy.named_parameters():
        params[name] = param.detach().cpu().numpy().tolist()

    path = "modeles/politique_raspberry.json"
    with open(path, "w") as f:
        json.dump(params, f)
    print(f"✅ Politique exportée pour Raspberry : {path}")


# ── Test du modèle sauvegardé ─────────────────────────────────
def tester():
    print("=" * 55)
    print("  Test du modèle PPO sauvegardé")
    print("=" * 55)

    try:
        model = PPO.load(f"{BEST_MODEL_PATH}/best_model")
        print("✅ Meilleur modèle chargé.")
    except Exception:
        model = PPO.load(MODEL_PATH)
        print("✅ Modèle final chargé.")

    env = MatchEnv()
    scores_total = []

    for ep in range(10):
        obs, _ = env.reset()
        ep_reward = 0
        done = False
        actions_prises = []

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(int(action))
            ep_reward += reward
            done = terminated or truncated
            actions_prises.append(int(action))

        scores_total.append(env.score)
        print(f"  Épisode {ep+1:2d} | Score: {env.score:5.1f} pts | "
              f"Reward: {ep_reward:+7.2f} | "
              f"Zones visitées: {sum(env.zones_visitees)}/9 | "
              f"Nid: {'✅' if env.nid_atteint else '❌'}")

    print(f"\n  Score moyen sur 10 épisodes : {np.mean(scores_total):.1f} pts")
    print(f"  Score max                   : {np.max(scores_total):.1f} pts")
    env.close()


# ── Inférence légère pour Raspberry Pi ───────────────────────
def inferer_raspberry(obs_dict, json_path="modeles/politique_raspberry.json"):
    """
    Inférence manuelle depuis le JSON exporté.
    À copier sur la Raspberry — pas besoin de SB3 ni PyTorch.

    obs_dict : dict avec les clés de l'observation (voir MatchEnv._get_obs)
    Retourne : int (index de l'action choisie)
    """
    import json as _json, math as _math

    with open(json_path) as f:
        params = _json.load(f)

    def dense(x, W, b):
        out = []
        for j in range(len(b)):
            s = sum(x[i] * W[j][i] for i in range(len(x))) + b[j]
            out.append(_math.tanh(s))
        return out

    def softmax(x):
        ex = [_math.exp(v - max(x)) for v in x]
        s  = sum(ex)
        return [v/s for v in ex]

    # Forward pass (réseau MlpPolicy SB3 standard)
    x = list(obs_dict.values())
    x = dense(x,
              params["mlp_extractor.policy_net.0.weight"],
              params["mlp_extractor.policy_net.0.bias"])
    x = dense(x,
              params["mlp_extractor.policy_net.2.weight"],
              params["mlp_extractor.policy_net.2.bias"])
    logits = dense(x,
                   params["action_net.weight"],
                   params["action_net.bias"])
    probs  = softmax(logits)
    return probs.index(max(probs))


# ── Point d'entrée ────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true",
                        help="Tester le modèle sauvegardé au lieu d'entraîner")
    args = parser.parse_args()

    if args.test:
        tester()
    else:
        entrainer()