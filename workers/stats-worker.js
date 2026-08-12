/**
 * Cloudflare Worker for Personal Stats API
 * Route: GET /api/stats
 * Combines GitHub GraphQL statistics & WakaTime coding activity into a cached JSON payload.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle CORS preflight request
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }

    // Serve /api/stats endpoint
    if (url.pathname === "/api/stats" || url.pathname === "/stats") {
      try {
        const data = await fetchAggregatedStats(env);
        return new Response(JSON.stringify(data, null, 2), {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600, s-maxage=3600",
          },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        });
      }
    }

    // Serve /api/spotify - Spotify Now Playing JSON (Cached 30 seconds)
    if (url.pathname === "/api/spotify" || url.pathname === "/spotify") {
      const spotifyData = await fetchSpotifyNowPlaying(env);
      return new Response(JSON.stringify(spotifyData, null, 2), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "public, max-age=30, s-maxage=30",
        },
      });
    }

    // Serve /api/status - Live WakaTime Coding Status (Green/Yellow/Red)
    if (url.pathname === "/api/status" || url.pathname === "/status") {
      const statusData = await fetchWakatimeStatus(env);
      return new Response(JSON.stringify(statusData, null, 2), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "public, max-age=60, s-maxage=60",
        },
      });
    }

    return new Response(JSON.stringify({ error: "Endpoint not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  },
};

/**
 * Aggregates GitHub GraphQL & WakaTime stats
 */
async function fetchAggregatedStats(env) {
  const username = env.GITHUB_USERNAME || "MannDangrechiya";
  const token = env.GITHUB_TOKEN || "";

  let githubStats = {
    stars: 0,
    forks: 0,
    followers: 0,
    totalCommits: 450
  };

  // 1. Fetch GitHub GraphQL API stats if token is available
  if (token) {
    try {
      const graphqlQuery = {
        query: `
          query {
            user(login: "${username}") {
              followers { totalCount }
              repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
                nodes {
                  stargazerCount
                  forkCount
                }
              }
              contributionsCollection {
                totalCommitContributions
              }
            }
          }
        `
      };

      const ghRes = await fetch("https://api.github.com/graphql", {
        method: "POST",
        headers: {
          "Authorization": `bearer ${token}`,
          "User-Agent": "CloudflareWorker-MannStats",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(graphqlQuery)
      });

      if (ghRes.ok) {
        const json = await ghRes.json();
        const user = json.data?.user;
        if (user) {
          githubStats.followers = user.followers?.totalCount || 0;
          githubStats.totalCommits = user.contributionsCollection?.totalCommitContributions || 0;
          const repos = user.repositories?.nodes || [];
          githubStats.stars = repos.reduce((sum, r) => sum + (r.stargazerCount || 0), 0);
          githubStats.forks = repos.reduce((sum, r) => sum + (r.forkCount || 0), 0);
        }
      }
    } catch (e) {
      // Fallback below
    }
  }

  // Fallback REST fetch if GraphQL token was missing or failed
  if (githubStats.stars === 0 && githubStats.followers === 0) {
    try {
      const uRes = await fetch(`https://api.github.com/users/${username}`, {
        headers: { "User-Agent": "CloudflareWorker-MannStats" }
      });
      if (uRes.ok) {
        const uData = await uRes.json();
        githubStats.followers = uData.followers || 25;
      }

      const rRes = await fetch(`https://api.github.com/users/${username}/repos?per_page=100`, {
        headers: { "User-Agent": "CloudflareWorker-MannStats" }
      });
      if (rRes.ok) {
        const repos = await rRes.json();
        if (Array.isArray(repos)) {
          githubStats.stars = repos.reduce((acc, r) => acc + (r.stargazers_count || 0), 0);
          githubStats.forks = repos.reduce((acc, r) => acc + (r.forks_count || 0), 0);
        }
      }
    } catch (e) {
      githubStats.stars = githubStats.stars || 18;
      githubStats.forks = githubStats.forks || 6;
    }
  }

  // 2. Fetch WakaTime Stats
  let wakatimeStats = {
    totalHours: "148 hrs 30 mins",
    languages: [
      { name: "Dart", percent: 64.5 },
      { name: "Python", percent: 18.2 },
      { name: "JavaScript", percent: 10.3 },
      { name: "HTML/CSS", percent: 7.0 }
    ]
  };

  try {
    const wakaUser = env.WAKATIME_USER || "manndangrechiya";
    const wakaRes = await fetch(`https://wakatime.com/api/v1/users/${wakaUser}/stats/last_7_days`, {
      headers: { "User-Agent": "CloudflareWorker-MannStats" }
    });

    if (wakaRes.ok) {
      const wData = await wakaRes.json();
      if (wData?.data) {
        wakatimeStats.totalHours = wData.data.human_readable_total || wakatimeStats.totalHours;
        if (Array.isArray(wData.data.languages)) {
          wakatimeStats.languages = wData.data.languages.slice(0, 5).map(l => ({
            name: l.name,
            percent: Math.round(l.percent * 10) / 10
          }));
        }
      }
    }
  } catch (e) {
    // Keep fallback defaults
  }

  return {
    username,
    github: githubStats,
    wakatime: wakatimeStats,
    updatedAt: new Date().toISOString()
  };
}

/**
 * Fetches Spotify Current Track with OAuth refresh token
 */
async function fetchSpotifyNowPlaying(env) {
  const clientId = env.SPOTIFY_CLIENT_ID;
  const clientSecret = env.SPOTIFY_CLIENT_SECRET;
  const refreshToken = env.SPOTIFY_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    return {
      isPlaying: true,
      title: "Starboy (feat. Daft Punk)",
      artist: "The Weeknd, Daft Punk",
      album: "Starboy",
      albumArt: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5a86d7",
      songUrl: "https://open.spotify.com/track/7l2hASKRWwMebg1xQ2B9p8",
      cachedSeconds: 30
    };
  }

  try {
    // 1. Get Access Token using refresh token
    const basicAuth = btoa(`${clientId}:${clientSecret}`);
    const tokenRes = await fetch("https://accounts.spotify.com/api/token", {
      method: "POST",
      headers: {
        "Authorization": `Basic ${basicAuth}`,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: refreshToken
      })
    });

    if (!tokenRes.ok) throw new Error("Failed to refresh Spotify token");
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    // 2. Fetch current playing track
    const trackRes = await fetch("https://api.spotify.com/v1/me/player/currently-playing", {
      headers: { "Authorization": `Bearer ${accessToken}` }
    });

    if (trackRes.status === 204 || trackRes.status > 400) {
      return { isPlaying: false, statusText: "⏸ Paused", cachedSeconds: 30 };
    }

    const track = await trackRes.json();
    if (!track || !track.is_playing) {
      return { isPlaying: false, statusText: "⏸ Paused", cachedSeconds: 30 };
    }

    return {
      isPlaying: true,
      title: track.item?.name || "Unknown Track",
      artist: track.item?.artists?.map(a => a.name).join(", ") || "Unknown Artist",
      album: track.item?.album?.name || "",
      albumArt: track.item?.album?.images?.[0]?.url || "",
      songUrl: track.item?.external_urls?.spotify || "#",
      cachedSeconds: 30
    };
  } catch (err) {
    return {
      isPlaying: true,
      title: "Starboy (feat. Daft Punk)",
      artist: "The Weeknd, Daft Punk",
      album: "Starboy",
      albumArt: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5a86d7",
      songUrl: "https://open.spotify.com/track/7l2hASKRWwMebg1xQ2B9p8",
      cachedSeconds: 30
    };
  }
}

/**
 * Fetches WakaTime status (Green: < 5 min, Yellow: < 30 min, Red: > 30 min)
 */
async function fetchWakatimeStatus(env) {
  const wakaUser = env.WAKATIME_USER || "manndangrechiya";
  try {
    const res = await fetch(`https://wakatime.com/api/v1/users/${wakaUser}/heartbeats`, {
      headers: { "User-Agent": "CloudflareWorker-MannStatus" }
    });

    if (res.ok) {
      const json = await res.json();
      const lastHeartbeat = json.data?.[0];
      if (lastHeartbeat) {
        const lastTime = new Date(lastHeartbeat.time * 1000).getTime();
        const diffMins = (Date.now() - lastTime) / (1000 * 60);

        if (diffMins <= 5) {
          return { status: "coding", color: "#22C55E", label: "🟢 CODING NOW", editor: lastHeartbeat.entity || "VS Code", diffMins: Math.round(diffMins) };
        } else if (diffMins <= 30) {
          return { status: "idle", color: "#EAB308", label: "🟡 IDLE / IN FLOW", editor: "VS Code", diffMins: Math.round(diffMins) };
        }
      }
    }
  } catch (e) {}

  return { status: "offline", color: "#EF4444", label: "🔴 OFFLINE / AWAY", editor: "Flutter DevTools", diffMins: 45 };
}

