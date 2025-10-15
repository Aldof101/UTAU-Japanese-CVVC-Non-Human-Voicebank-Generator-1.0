import os
import wave
import math
import array
from datetime import datetime

# Define paths
consonant_path = r"this\is\a\PATH"
vowel_path = r"this\is\a\PATH"
output_path = r"this\is\a\PATH"

# Ensure output directory exists
os.makedirs(output_path, exist_ok=True)

# Vowel list
vowels = ['a', 'e', 'u', 'i', 'o', 'n']

# Recording table
recording_table = [
    "a_i_u_e_o_a",
    "a_u_o_i_e_a",
    "a_e_i_o_u_a",
    "a_o_e_u_i_a",
    "a_i_u_e_o_n",
    "ka_ki_ku_ke_ko_kya_kyu_kye_kyo",
    "ga_gi_gu_ge_go_gya_gyu_gye_gyo",
    "nga_ngi_ngu_nge_ngo_ngya_ngyu_ngye_ngyo",
    "sa_si_su_se_so",
    "za_zi_zu_ze_zo",
    "sha_shi_shu_she_sho",
    "ja_ji_ju_je_jo",
    "tsa_tsi_tsu_tse_tso",
    "dza_dzi_dzu_dze_dzo",
    "cha_chi_chu_che_cho",
    "dja_dji_dju_dje_djo",
    "ta_ti_tu_te_to_tya_tyu_tye_tyo",
    "da_di_du_de_do_dya_dyu_dye_dyo",
    "pa_pi_pu_pe_po_pya_pyu_pye_pyo",
    "ba_bi_bu_be_bo_bya_byu_bye_byo",
    "fa_fi_fu_fe_fo_fya_fyu_fye_fyo",
    "ma_mi_mu_me_mo_mya_myu_mye_myo",
    "ra_ri_ru_re_ro_rya_ryu_rye_ryo",
    "ya_yi_yu_ye_yo",
    "wa_wi_wu_we_wo",
    "va_vi_vu_ve_vo",
    "ha_hi_hu_he_ho",
    "hya_hyi_hyu_hye_hyo",
    "na_ni_nu_ne_no",
    "nya_nyi_nyu_nye_nyo",
    "jya_jyu_jye_jyo",
    "sya_syi_syu_sye_syo",
    "kwa_kwi_kwu_kwe_kwo_ka",
    "gwa_gwi_gwu_gwe_gwo_ga",
    "rwa_rwi_rwu_rwe_rwo_ra"
]

def read_wav(file_path):
    """Read WAV file, return audio data and parameters"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)
            # Convert byte data to array
            if params.sampwidth == 2:
                audio_data = array.array('h', frames)
            else:
                # If not 16-bit, need to convert
                raise ValueError("Only 16-bit audio is supported")
            return audio_data, params
    except Exception as e:
        raise Exception(f"Cannot read file {file_path}: {str(e)}")

def write_wav(file_path, audio_data, params):
    """Write audio data to WAV file"""
    try:
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setparams(params)
            # Convert array to byte data
            wav_file.writeframes(audio_data.tobytes())
    except Exception as e:
        raise Exception(f"Cannot write file {file_path}: {str(e)}")

def apply_cosine_fadeout(audio_data, fade_fraction=0.3):
    """Apply cosine fadeout to the last fade_fraction of audio data"""
    if len(audio_data) == 0:
        return audio_data
    
    fade_samples = int(len(audio_data) * fade_fraction)
    if fade_samples == 0:
        fade_samples = 1
    
    result = array.array('h', audio_data)
    
    # Apply cosine fadeout to the last fade_fraction of audio
    for i in range(fade_samples):
        index = len(audio_data) - fade_samples + i
        if index < len(audio_data):
            # Calculate cosine fade factor (1.0 to 0.0)
            # Using cosine curve for smoother fadeout
            fade_factor = math.cos((i / fade_samples) * (math.pi / 2))
            # Apply fade
            faded_sample = int(result[index] * fade_factor)
            result[index] = max(-32768, min(32767, faded_sample))
    
    return result

def cosine_crossfade_segments(audio1, audio2, crossfade_fraction=0.05):
    """Apply cosine crossfade between two audio segments"""
    if len(audio1) == 0:
        return audio2
    if len(audio2) == 0:
        return audio1
    
    # Calculate crossfade length (5% of each segment)
    crossfade_len1 = int(len(audio1) * crossfade_fraction)
    crossfade_len2 = int(len(audio2) * crossfade_fraction)
    
    # Use the smaller crossfade length
    crossfade_length = min(crossfade_len1, crossfade_len2)
    
    # Ensure minimum crossfade length
    crossfade_length = max(10, crossfade_length)
    
    # If crossfade length is too large, reduce it
    if crossfade_length > len(audio1) or crossfade_length > len(audio2):
        crossfade_length = min(len(audio1), len(audio2)) // 2
        crossfade_length = max(10, crossfade_length)
    
    result = array.array('h')
    
    # Add first segment without the crossfade portion
    if len(audio1) > crossfade_length:
        result.extend(audio1[:-crossfade_length])
    
    # Apply cosine crossfade
    for i in range(crossfade_length):
        if (len(audio1) - crossfade_length + i) < len(audio1) and i < len(audio2):
            # Calculate cosine fade factors
            # First audio fades out using cosine curve
            factor1 = math.cos((i / crossfade_length) * (math.pi / 2))
            # Second audio fades in using sine curve (complement of cosine)
            factor2 = math.sin((i / crossfade_length) * (math.pi / 2))
            
            # Apply crossfade
            sample1 = audio1[len(audio1) - crossfade_length + i] if (len(audio1) - crossfade_length + i) < len(audio1) else 0
            sample2 = audio2[i] if i < len(audio2) else 0
            sample = int(sample1 * factor1 + sample2 * factor2)
            result.append(sample)
    
    # Add remaining part of second segment
    if crossfade_length < len(audio2):
        result.extend(audio2[crossfade_length:])
    
    return result

def concatenate_audio(consonant_data, vowel_data, params):
    """Concatenate consonant and vowel audio"""
    # Calculate 55% position of consonant
    consonant_cut_pos = int(len(consonant_data) * 0.55)
    
    # Extract first 55% of consonant
    consonant_part = consonant_data[:consonant_cut_pos]
    
    # Calculate fade length (10% of shorter audio)
    fade_length = min(int(len(consonant_data) * 0.1), int(len(vowel_data) * 0.1))
    fade_length = max(10, fade_length)  # Ensure at least 10 samples
    
    # Crossfade between remaining consonant and vowel
    consonant_remainder = consonant_data[consonant_cut_pos:]
    faded_part = cosine_crossfade_segments(consonant_remainder, vowel_data, 0.1)  # Use 10% for consonant-vowel crossfade
    
    # Concatenate audio
    result = array.array('h')
    result.extend(consonant_part)
    result.extend(faded_part)
    
    return result

def process_syllable(syllable, error_report):
    """Process a single syllable and return audio data"""
    # Check if it's a pure vowel
    if syllable in vowels:
        # Directly use vowel file
        vowel_file = os.path.join(vowel_path, f"{syllable}.wav")
        if os.path.exists(vowel_file):
            try:
                vowel_data, params = read_wav(vowel_file)
                print(f"Loaded vowel: {syllable}")
                return vowel_data, params
            except Exception as e:
                error_report.append(f"Error processing vowel {syllable}: {str(e)}")
                return None, None
        else:
            error_msg = f"Vowel file not found: {vowel_file}"
            error_report.append(error_msg)
            print(f"Warning: {error_msg}")
            return None, None
    
    # Separate consonant and vowel parts
    consonant_part = None
    vowel_part = None
    
    # Try different consonant lengths (from long to short)
    for i in range(min(4, len(syllable)), 0, -1):
        consonant_candidate = syllable[:i]
        vowel_candidate = syllable[i:]
        
        if vowel_candidate in vowels:
            consonant_part = consonant_candidate
            vowel_part = vowel_candidate
            break
    
    if consonant_part is None or vowel_part is None:
        error_msg = f"Cannot parse syllable: {syllable}"
        error_report.append(error_msg)
        print(f"Warning: {error_msg}")
        return None, None
    
    # Build consonant filename
    consonant_file = os.path.join(consonant_path, f"{consonant_part}-.wav")
    vowel_file = os.path.join(vowel_path, f"{vowel_part}.wav")
    
    # Check if files exist
    if not os.path.exists(consonant_file):
        error_msg = f"Consonant file not found: {consonant_file}"
        error_report.append(error_msg)
        print(f"Warning: {error_msg}")
        return None, None
    
    if not os.path.exists(vowel_file):
        error_msg = f"Vowel file not found: {vowel_file}"
        error_report.append(error_msg)
        print(f"Warning: {error_msg}")
        return None, None
    
    try:
        # Read audio files
        consonant_data, consonant_params = read_wav(consonant_file)
        vowel_data, vowel_params = read_wav(vowel_file)
        
        # Ensure parameters match
        if consonant_params.sampwidth != 2 or vowel_params.sampwidth != 2:
            error_msg = f"Audio is not 16-bit format: {syllable}"
            error_report.append(error_msg)
            print(f"Warning: {error_msg}")
            return None, None
        
        if consonant_params.nchannels != 1 or vowel_params.nchannels != 1:
            error_msg = f"Audio is not mono: {syllable}"
            error_report.append(error_msg)
            print(f"Warning: {error_msg}")
            return None, None
        
        if consonant_params.framerate != 44100 or vowel_params.framerate != 44100:
            error_msg = f"Audio sample rate is not 44100Hz: {syllable}"
            error_report.append(error_msg)
            print(f"Warning: {error_msg}")
            return None, None
        
        # Concatenate audio
        combined_audio = concatenate_audio(consonant_data, vowel_data, consonant_params)
        
        print(f"Processed: {syllable}")
        return combined_audio, consonant_params
    except Exception as e:
        error_msg = f"Error processing syllable {syllable}: {str(e)}"
        error_report.append(error_msg)
        print(f"Error: {error_msg}")
        return None, None

def process_recording_line(line, error_report):
    """Process a line from recording table and create combined audio file"""
    syllables = line.split('_')
    syllable_audios = []
    params = None
    
    # Process each syllable in the line
    for syllable in syllables:
        audio_data, audio_params = process_syllable(syllable, error_report)
        if audio_data is not None and audio_params is not None:
            # Apply cosine fadeout to the last 30% of each syllable
            faded_audio = apply_cosine_fadeout(audio_data, 0.3)
            syllable_audios.append(faded_audio)
            if params is None:
                params = audio_params
        else:
            error_report.append(f"Failed to process syllable {syllable} in line {line}")
            return False
    
    if not syllable_audios:
        error_report.append(f"No valid syllables processed for line {line}")
        return False
    
    # Concatenate all syllables with cosine crossfade between them
    combined_audio = syllable_audios[0]
    
    for i in range(1, len(syllable_audios)):
        combined_audio = cosine_crossfade_segments(combined_audio, syllable_audios[i], 0.05)
    
    # Write output file
    output_file = os.path.join(output_path, f"{line}.wav")
    try:
        write_wav(output_file, combined_audio, params)
        print(f"Generated: {output_file}")
        return True
    except Exception as e:
        error_msg = f"Error writing file {output_file}: {str(e)}"
        error_report.append(error_msg)
        print(f"Error: {error_msg}")
        return False

def generate_error_report(error_report):
    """Generate error report"""
    if not error_report:
        return
    
    # Create error report file
    report_file = os.path.join(output_path, f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Audio Concatenation Error Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total errors: {len(error_report)}\n\n")
        
        for i, error in enumerate(error_report, 1):
            f.write(f"{i}. {error}\n")
    
    print(f"\nError report generated: {report_file}")

def main():
    """Main function"""
    print("Starting audio concatenation...")
    
    # Initialize error report
    error_report = []
    processed_count = 0
    error_count = 0
    
    # Process all lines in recording table
    for line in recording_table:
        if process_recording_line(line, error_report):
            processed_count += 1
        else:
            error_count += 1
    
    # Generate error report
    generate_error_report(error_report)
    
    print(f"\nProcessing complete! Successful: {processed_count}, Failed: {error_count}")

if __name__ == "__main__":
    main()