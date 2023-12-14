# https://github.com/ArthurFDLR/whisper-youtube
import sys
import warnings
import whisper
from pathlib import Path
import yt_dlp
import subprocess
import torch
import shutil
import numpy as np
from IPython.display import display, Markdown, YouTubeVideo



Model = 'medium' #@param ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large']
Model = 'tiny' 

whisper_model = whisper.load_model(Model)






URL = "https://www.youtube.com/watch?v=Z8yL3zkudZU"


video_path_local_list = []



ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download([URL])
    list_video_info = [ydl.extract_info(URL, download=False)]

for video_info in list_video_info:
    video_path_local_list.append(Path(f"{video_info['id']}.wav"))



for video_path_local in video_path_local_list:
    if video_path_local.suffix == ".mp4":
        video_path_local = video_path_local.with_suffix(".wav")
        result  = subprocess.run(["ffmpeg", "-i", str(video_path_local.with_suffix(".mp4")), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(video_path_local)])


#@markdown # **Run the model** 🚀

#@markdown Run this cell to execute the transcription of the video. This can take a while and very based on the length of the video and the number of parameters of the model selected above.

#@markdown ## **Parameters** ⚙️

#@markdown ### **Behavior control**
#@markdown ---
language = "Auto detection" #@param ['Auto detection', 'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Assamese', 'Azerbaijani', 'Bashkir', 'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Castilian', 'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Faroese', 'Finnish', 'Flemish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian', 'Haitian Creole', 'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Javanese', 'Kannada', 'Kazakh', 'Khmer', 'Korean', 'Lao', 'Latin', 'Latvian', 'Letzeburgesch', 'Lingala', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Maltese', 'Maori', 'Marathi', 'Moldavian', 'Moldovan', 'Mongolian', 'Myanmar', 'Nepali', 'Norwegian', 'Nynorsk', 'Occitan', 'Panjabi', 'Pashto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Pushto', 'Romanian', 'Russian', 'Sanskrit', 'Serbian', 'Shona', 'Sindhi', 'Sinhala', 'Sinhalese', 'Slovak', 'Slovenian', 'Somali', 'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tagalog', 'Tajik', 'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uzbek', 'Valencian', 'Vietnamese', 'Welsh', 'Yiddish', 'Yoruba']
#@markdown > Language spoken in the audio, use `Auto detection` to let Whisper detect the language.
#@markdown ---
verbose = 'Live transcription' #@param ['Live transcription', 'Progress bar', 'None']
#@markdown > Whether to print out the progress and debug messages.
#@markdown ---
output_format = 'tsv' #@param ['txt', 'vtt', 'srt', 'tsv', 'json', 'all']
#@markdown > Type of file to generate to record the transcription.
#@markdown ---
task = 'transcribe' #@param ['transcribe', 'translate']
#@markdown > Whether to perform X->X speech recognition (`transcribe`) or X->English translation (`translate`).
#@markdown ---

#@markdown <br/>

#@markdown ### **Optional: Fine tunning**
#@markdown ---
temperature = 0.15 #@param {type:"slider", min:0, max:1, step:0.05}
#@markdown > Temperature to use for sampling.
#@markdown ---
temperature_increment_on_fallback = 0.2 #@param {type:"slider", min:0, max:1, step:0.05}
#@markdown > Temperature to increase when falling back when the decoding fails to meet either of the thresholds below.
#@markdown ---
best_of = 5 #@param {type:"integer"}
#@markdown > Number of candidates when sampling with non-zero temperature.
#@markdown ---
beam_size = 8 #@param {type:"integer"}
#@markdown > Number of beams in beam search, only applicable when temperature is zero.
#@markdown ---
patience = 1.0 #@param {type:"number"}
#@markdown > Optional patience value to use in beam decoding, as in [*Beam Decoding with Controlled Patience*](https://arxiv.org/abs/2204.05424), the default (1.0) is equivalent to conventional beam search.
#@markdown ---
length_penalty = 1 #@param {type:"slider", min:-0.05, max:1, step:0.05}
#@markdown > Optional token length penalty coefficient (alpha) as in [*Google's Neural Machine Translation System*](https://arxiv.org/abs/1609.08144), set to negative value to uses simple length normalization.
#@markdown ---
suppress_tokens = "-1" #@param {type:"string"}
#@markdown > Comma-separated list of token ids to suppress during sampling; '-1' will suppress most special characters except common punctuations.
#@markdown ---
initial_prompt = "" #@param {type:"string"}
#@markdown > Optional text to provide as a prompt for the first window.
#@markdown ---
condition_on_previous_text = True #@param {type:"boolean"}
#@markdown > if True, provide the previous output of the model as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop.
#@markdown ---
fp16 = True #@param {type:"boolean"}
#@markdown > whether to perform inference in fp16.
#@markdown ---
compression_ratio_threshold = 2.4 #@param {type:"number"}
#@markdown > If the gzip compression ratio is higher than this value, treat the decoding as failed.
#@markdown ---
logprob_threshold = -1.0 #@param {type:"number"}
#@markdown > If the average log probability is lower than this value, treat the decoding as failed.
#@markdown ---
no_speech_threshold = 0.6 #@param {type:"slider", min:-0.0, max:1, step:0.05}
#@markdown > If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence.
#@markdown ---

verbose_lut = {
    'Live transcription': True,
    'Progress bar': False,
    'None': None
}

args = dict(
    language = (None if language == "Auto detection" else language),
    verbose = verbose_lut[verbose],
    task = task,
    temperature = temperature,
    temperature_increment_on_fallback = temperature_increment_on_fallback,
    best_of = best_of,
    beam_size = beam_size,
    patience=patience,
    length_penalty=(length_penalty if length_penalty>=0.0 else None),
    suppress_tokens=suppress_tokens,
    initial_prompt=(None if not initial_prompt else initial_prompt),
    condition_on_previous_text=condition_on_previous_text,
    fp16=fp16,
    compression_ratio_threshold=compression_ratio_threshold,
    logprob_threshold=logprob_threshold,
    no_speech_threshold=no_speech_threshold
)

temperature = args.pop("temperature")
temperature_increment_on_fallback = args.pop("temperature_increment_on_fallback")
if temperature_increment_on_fallback is not None:
    temperature = tuple(np.arange(temperature, 1.0 + 1e-6, temperature_increment_on_fallback))
else:
    temperature = [temperature]

if Model.endswith(".en") and args["language"] not in {"en", "English"}:
    warnings.warn(f"{Model} is an English-only model but receipted '{args['language']}'; using English instead.")
    args["language"] = "en"

for video_path_local in video_path_local_list:
    display(Markdown(f"### {video_path_local}"))

    video_transcription = whisper.transcribe(
        whisper_model,
        str(video_path_local),
        temperature=temperature,
        **args,
    )

    # Save output
    whisper.utils.get_writer(
        output_format=output_format,
        output_dir=video_path_local.parent
    )(
        video_transcription,
        str(video_path_local.stem),
        options=dict(
            highlight_words=False,
            max_line_count=None,
            max_line_width=None,
        )
    )

