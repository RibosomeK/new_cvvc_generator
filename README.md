
# A Simple CVVC Reclist Generator With GUI

[English](#en), [简体中文](#cn)

<span id="en"></span>

## Main Feature:
- with GUI
- compatible with VocalSharp (early support)
- needed alias can be manipulated relatively easy
- have a preview for generated outcomes


## Usage (Basic):
1. select a dict file
2. chose the outline of reclist style, whether is Haru.J or multi mora
3. decide how many words in a line if multi mora is selected
4. tick whatever file you want to save down below
5. preview if you like or click save to generate.


## Parameters Explain:

### Dict File:
dict file is a plain text with the following structure:
> CVC C V C_alias V_alias CV

CVC is the whole word such as [biao] in Mandarin, [か] in Japanese. [biao] will be used as a sample in the following.

C is the consonant. As for [biao], it can be [b] in most UTAU practices or [by] in VocalSharp

V is the vowel. It can be [ao] in UTAU or [iao] in VocalSharp. It depends.

CV can be unified or simplified cv part. For example, [biA] and be a unified cv for both [biao] and [biang] if you like.

`biao b ao by ao biA
`

separation symbol can be a half-width space, comma or semi-comma, a tab, full-width comma or semi-comma

The C_alias and V_alias will not be used in redirecting in this stage, only in VocalSharp dict file *.lsd.

### Redirect Config:
A ini style config specific for VocalSharp, do not competitive with the official redirect file. Multiple redirect files selected at once is also supported. It has two sections: [VOWEL] and [CONSONANT] and the following syntax

> REDIRECT=ALIAS1,ALIAS2...

For example, `t=tw,ty` will generator `tw,#t,0,0,0,0,0` and `ty,#t,0,0,0,0,0` in VocalSharp labelling file.

### Alias Config:
A json style config to add needed alias and eliminate unwanted alias. By adding alias quote by double quotes in square brackets, separated by half-width comma.
For example, if you want to include vcv for some consonants that tricky to cvvc splicing, take [j] and [z] for example, you can filling like this:

```json
    "NEEDED": {
        "VCV": {
            "v": [],
            "c": ["j", "q"],
            "vcv": []
        }
    }
```

To specific certain vcv, like [aap z], [aat z], [aak z], add like this: 

```json
    "NEEDED": {
        "VCV": {
            "v": [],
            "c": [],
            "vcv": ["aap z", "aat z", "aak z"]
        }
    }
```

Other is the same.

The priority in "UNNEEDED" is higher. Which means alias in both "NEEDED" and "UNNEEDED" will be eliminated. Generated reclist will not include such an alias.

### Reclist Style:
2 mora means two words in a line, mora x is more than 2, specific length can be selected in Reclist Detail.

Haru.J style include long note sample for cv, labeled by "_L". For detail description, see [Hr.J式CVVC中文录音方案介绍](https://utaujc.jimdofree.com/hr-j-cvvc/)

Hr.J style and be used with other reclist style. But 2 mora and mora x is conflict.

### Reclist Detail:
- Length: how many words in one line, conflict with 2 mora
- CV head: include beginning cv or not. Default is true
- Full cv: use whole cv instead of unified cv in cv, cv head or vcv. Default is true
- C head for UTAU: include c head for utau. Default is false

### Labeling Style:
- bpm: the bpm of recording bgm. Default is 130, step is 10
- blank beat: how many beat before voicing. Default is 2, used by One Note Jazz bgm series

### Save Path:
A save path for generated outcomes. Default is "./result"

Different folder for different reclist outcomes is recommended.

### Other Functions:
- you can save and load the parameters setting into a config in "File" menu
- undo and redo in selecting files is supported to function as loading a unnecessary file
- translation currently support English and Simplified Chinese

## Known Issus:
1. tests are needed
2. my poor English and Python
3. can't undo loading a config
4. un完全 translation for Chinese

## Todo (might):
1. complete translation
2. ~~add multi-redirect-file function~~
3. you name it (Will anyone actually use it?)

## Contact:
- mail: ribosomek_khaki@gmail.com

## Special Thanks and Credits
- Risku for mandarin cvvc scheme
- Haru.J for Hr.J cvvc scheme
- 金刚, the author of VocalSharp
- Qt for Python, The Qt Company Ltd, for GUI
- [Pyinstaller](https://pyinstaller.org/) for packing into an executable file

<br>
<br>
<span id="cn"></span>

## 主要特性：
- 附带图形界面
- 可以生成 VocalSharp 标记和字典文件（早期支持）
- 可以通过配置文件增减需要的音素
- 可预览结果


## 基本使用方法：
1. 选择字典文件
2. 选择录音表的整体方案，是否包含Hr.J 式等
3. 如果是多字表，选择需要的字数
4. 勾选需要生成的文件，录音表、窝头、字典等
5. 点击生成按钮或者预览查看后再生成


## 参数介绍：

### 字典文件：
吐表机所用字典为纯文本， 格式如下
> CVC C V C_别名 V_别名 CV

CVC 指整音， 如普通话的 [biao]，日文的 [か]。[biao] 会被用作例子

C 指辅音。对于 [biao] 来说，在 UTAU 中一般用 [b] 指代，而在 VocalSharp 中可以选择使用 [by]

V 指元音，在 UTAU 中一般用 [ao]，而 VocalSharp 中可以选择用 [iao] 做区分

CV 可以用来合并某些整音的 cv 部，如 [biA] 可以用来代替 [biao] 和 [biang]

具体例子如下

> biao b ao by ao biA

每一行的分割符号可以用半角的空格、逗号、分号，全角的逗号、分号，制表符 tab

C_别名 和 V_别名 目前不会在 VocalSharp 窝头的重定向中使用，只会用于生成该引擎的字典

### 重定向文件：
用于 VocalSharp 窝头的重定向，使用 ini 格式，与官方的重定向配置不兼容。现在支持选择多个文件。配置中含有两个部分：[VOWEL] and [CONSONANT]，语法格式如下：

> 重定向至=别名1,别名2...

如，`t=tw,ty` 指 [tw] 和 [ty] 会被重定向至 [t]，生成如下标记：
```
tw,#t,0,0,0,0,0
ty,#t,0,0,0,0,0
``` 

### 别名文件：
json 格式的配置文件，可以在方括号内增减额外的音素，音素用半角双引号包起来

如果需要增加 vcv 音素，比如你觉得连起来的 [j] 和 [z] 很难做 vc 部，那你可以按照例子填入相应的音素

```json
    "NEEDED": {
        "VCV": {
            "v": [],
            "c": ["j", "q"],
            "vcv": []
        }
    }
```

如果要指定个别 vcv，可以这么填：

```json
    "NEEDED": {
        "VCV": {
            "v": [],
            "c": [],
            "vcv": ["aap z", "aat z", "aak z"]
        }
    }
```

其他都是一样的，分号前面是 v 就是指和这个元音相关的所有，c 就是和这个辅音相关的所有

"UNNEEDED" 的优先级会更高，也就是说只要你在这部分里包括了相对应的音素，就不会被生成

### 录音表样式：
两字和多字不能同时使用，两字会按顺序生成所需要的音素，而多字在生成时则是随机的。多字的长度可以在下面的字长选择

Haru.J 式会生成长音素，后缀为 "_L"。关于这个录音方案的介绍请参考 [Hr.J式CVVC中文录音方案介绍](https://utaujc.jimdofree.com/hr-j-cvvc/)

Haru.J 式可以与其他两个样式一起使用。

### 录音表详情：
- 字长：一行有多少字，不能和两字的样式一起使用
- 开头音：是否包含开头音，默认为包含
- 全整音：是否使用全整音而不是类似 [biA] 这种合并的在 cv 或者 vcv 中，默认使用全整音
- 开头辅音：是否在 UTAU oto 包含开头辅音，默认不包含

### 窝头详情：
- 录音曲速：录音用 BGM 的曲速，默认为 130
- 空白拍数：在出声念咒之前有多少拍，默认为 One Note Jazz 系列用的 2 拍

### 保存目录：
生成文件的保存目录，默认是同目录下的名叫 result 的文件夹里，"./result"

对于不同参数的录音表，推荐存放在不同的文件夹中

### 其他功能
- 可以在【文件】菜单中导出设置好参数的配置文件，用于下次导入
- 不小心选了多余的文件可以用【编辑】中的撤销来清空
- 目前的多语言只支持英文和简体中文，其他我不会捏

## 特别感谢和使用的第三方程式库：
- 首先提出中文 cvvc 录音方案的 Risku
- 提出 Hr.J 式 cvvc 录音方案的 Haru.J
- 金刚，VocalSharp 的作者
- Qt for Python, The Qt Company Ltd, 用于图形界面
- [Pyinstaller](https://pyinstaller.org/) 用来打包成可执行文件