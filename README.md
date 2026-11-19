# Pixel Uncovered – Android-first YouTube video factory

A zero-subscription starter project. Edit one JSON file from GitHub on your Android phone, run GitHub Actions, then download the generated MP4.

## What it does

- Creates original 1080x1920 vertical scene cards using Pillow.
- Generates narration using eSpeak NG.
- Assembles scenes and narration into an MP4 using FFmpeg.
- Produces a thumbnail, script and YouTube metadata text file.
- Saves outputs as a GitHub Actions artifact.

## Important limitations

This starter does **not** perform AI research, fact-checking, AI scriptwriting, realistic AI voices, or automatic YouTube publishing. It does not download other creators' gameplay. You provide the script and real source URLs in `content/episode.json`, verify claims and approve the final video. The generated voice is synthetic and somewhat robotic. This is deliberate: the basic pipeline has no paid API or subscription dependency.

GitHub Actions is free for standard runners in public repositories. Keep the repository public only if you are comfortable making your scripts and project files public; never put passwords, OAuth tokens or private information in it. GitHub's free private-repository allowance and billing limits can change, so check current limits before using a private repo.

## Android setup

1. Sign in to https://github.com/ and create a **public** repository named `pixel-uncovered-factory`.
2. Download this ZIP and extract it if your phone has an archive manager. Alternatively, use GitHub's web interface to create the files and paste their contents.
3. Upload the project files while preserving the folder structure. The `.github/workflows/build-video.yml` file must be in that exact path.
4. Open the repository's **Actions** tab.
5. If prompted, enable Actions.
6. Select **Build Pixel Uncovered video** and tap **Run workflow**.
7. Wait for the run to finish successfully.
8. Open the completed run and download the `pixel-uncovered-video` artifact.
9. Extract the artifact on your phone. Review the MP4, thumbnail, script and metadata.
10. Upload manually using YouTube Studio.

## Make a new episode

1. Open `content/episode.json` in your repository.
2. Tap the pencil/Edit button.
3. Change `topic`, `title`, `hook`, `scenes`, `description`, `hashtags` and `sources`.
4. Each scene needs:
   - `heading`: short on-screen heading
   - `caption`: short on-screen explanatory text
   - `narration`: the spoken words for that scene
5. Keep 4–7 scenes for a short video. Keep each caption concise.
6. Add reliable source URLs that support the claims. Do not leave placeholder URLs.
7. Commit the changes.
8. The workflow starts automatically after the content file is changed. You can also run it manually from Actions.

## Content quality and rights

- Use your own explanation, analysis and original writing.
- Verify every factual claim against reliable sources.
- Do not copy scripts from websites or other creators.
- Do not use copyrighted gameplay, music, logos or artwork unless you have permission or a licence that permits your intended commercial use.
- A free stock asset is not automatically cleared for every use; read its licence and retain attribution if required.
- Do not mass-produce interchangeable videos. Add original insight and meaningful variation.
- Do not buy views, subscribers or engagement.

## Troubleshooting

- **Workflow does not appear:** confirm `.github/workflows/build-video.yml` exists on the default branch and Actions are enabled.
- **Build fails:** open the failed run, expand the red step and read the last error lines.
- **No voice:** confirm the workflow installed `espeak-ng`; rerun the workflow.
- **Video is too long:** shorten narration or use fewer scenes.
- **Text overflows:** shorten the heading/caption.
- **Artifact missing:** the build step must finish successfully before upload-artifact runs.

## File layout

```text
pixel-uncovered-factory/
├── .github/workflows/build-video.yml
├── content/episode.json
├── output/
├── build.py
├── requirements.txt
└── README.md
```
