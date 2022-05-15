import librosa
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import soundfile as sf
import matplotlib.ticker

def STFT(signal,window,step):
    Z = []
    win_fc=np.hamming(window)
    for i in range((signal.shape[0] - window) // step):
        tmp = signal[i*step : i*step + window]
        tmp = tmp * win_fc
        tmp = np.fft.fft(tmp)
        Z.append(tmp)
    Z= np.array(Z)
    return Z

def ISTFT(y,frame_length,window,step):
    Z = np.zeros(frame_length)
    for i in range(len(y)) :
        tmp = np.fft.ifft(y[i])
        Z[i*step : i*step + window] += np.real(tmp)
    Z= np.array(Z)
    return Z


def HPF(fq,sr,fir_size = 512):
    pi = np.pi
    omega = 2 * pi * fq / sr
    arange = np.arange(-fir_size//2,fir_size//2)
    print(arange)
    filter = np.sinc(arange) - omega * np.sinc(omega*arange / pi)/pi
    window = np.hamming(fir_size)
    return filter * window


def LPF(fq,sr,fir_size = 512):
    pi = np.pi
    omega = 2 * pi * fq / sr
    arange = np.arange(-fir_size//2,fir_size//2)
    filter = omega * np.sinc(omega*arange / pi)/pi
    window = np.hamming(fir_size)
    return filter * window


def convolution(input,filter):
    input_len = len(input)
    filter_len = len(filter)
    result = np.zeros(input_len + filter_len - 1, dtype=np.complex128)

    for i in range(input_len):
        result[i : i+filter_len] += np.multiply(input[i] , filter)

    return result


if __name__ == "__main__":
    #load file
    file_name = "audio.wav"
    window = 1024
    step = window//2

    #original_signal = 音声信号の値、sr=サンプリング周波数 を取得
    original_signal, sr = librosa.load(file_name,sr=None)
    frame_length = original_signal.shape[0]

    #時間軸
    time = np.arange(0,original_signal.shape[0]) / sr

    #STFT
    original_spec = STFT(original_signal,window,step)

    filter =HPF(1000,sr=sr)
    filter_p = np.fft.fft(filter)
    filtered_signal = convolution(original_signal,filter) #時間領域
    filtered_spec = STFT(filtered_signal,window,step) #周波数領域に変換

    #PLOT
    fig = plt.figure(figsize=(8,6))

    #Original Signal
    ax1 = fig.add_subplot(3,2,1)
    ax1.plot(time,original_signal)
    ax1.set_xlabel("Time[s]")
    ax1.set_ylabel("Sound Amplitude")
    ax1.set_title("Original Signal")

    #Originak Spectrogram
    ax2 = fig.add_subplot(3,2,2)
    spec_log = 20 * np.log10(np.abs(original_spec).T)[window // 2:] #dB
    im = ax2.imshow(spec_log,cmap='jet',extent = [0,original_signal.shape[0] // sr,0,sr // 2,] ,aspect="auto")
    ax2.set_yscale("log",base=2)
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax2.set_ylim([50,20000])
    ax2.set_xlabel('Time[s]')
    ax2.set_ylabel('Frequency[Hz]')
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes('right', '2%', pad=0.1)
    cbar = fig.colorbar(im, format='%+2.0f dB', cax=cax)
    cbar.set_label("Magnitude[dB]")
    ax2.set_title("Spectrogram")

    #Filter property
    ax3 = fig.add_subplot(3,2,3)
    #ax0.plot(np.linspace(-sr//2, sr // 2, len(hpf)),20 * np.log10(np.abs(hpf_p)))
    ax3.plot(np.linspace(0, sr // 2, len(filter) // 2),20 * np.log10(np.abs(filter_p[: len(filter) // 2])))
    ax3.set_xscale("log",base=2)
    ax3.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax3.set_xlabel("Frequency[Hz]")
    ax3.set_ylabel("Sound Amplitude")
    ax3.set_title("Filter Property")

    #Filtered Signal Spectrogram
    ax4 = fig.add_subplot(3,2,4)
    spec_log = 20 * np.log10(np.abs(filtered_spec).T)[window // 2:] #dB
    im = ax4.imshow(spec_log,cmap='jet',extent = [0,original_signal.shape[0] // sr,0,sr // 2,] ,aspect="auto")
    ax4.set_yscale("log",base=2)
    ax4.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax4.set_ylim([50,20000])
    ax4.set_xlabel('Time[s]')
    ax4.set_ylabel('Frequency[Hz]')
    ax4.set_title("Filtered Signal")
    divider = make_axes_locatable(ax4)
    cax = divider.append_axes('right', '2%', pad=0.1)
    cbar = fig.colorbar(im, format='%+2.0f dB', cax=cax)
    cbar.set_label("Magnitude[dB]")

    plt.tight_layout()
    plt.show()
    plt.close()