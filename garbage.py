{
  "metadata": {
    "kernelspec": {
      "language": "python",
      "display_name": "Python 3",
      "name": "python3"
    },
    "language_info": {
      "pygments_lexer": "ipython3",
      "nbconvert_exporter": "python",
      "version": "3.6.4",
      "file_extension": ".py",
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "name": "python",
      "mimetype": "text/x-python"
    }
  },
  "nbformat_minor": 4,
  "nbformat": 4,
  "cells": [
    {
      "cell_type": "markdown",
      "source": "# Garbage Classification using PyTorch\n\nGarbage segregation involves separating wastes according to how it's handled or processed. It's important for recycling as some materials are recyclable and others are not.\n\n\n![Garbage Bins](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwebstockreview.net%2Fimages%2Fgarbage-clipart-wastebin-16.png&f=1&nofb=1)\n\n\nIn this notebook we'll use PyTorch for classifying trash into various categories like metal, cardboard, etc.",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "Let us start by importing the libraries:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "import os\nimport torch\nimport torchvision\nfrom torch.utils.data import random_split\nimport torchvision.models as models\nimport torch.nn as nn\nimport torch.nn.functional as F",
      "metadata": {
        "_uuid": "d629ff2d2480ee46fbb7e2d37f6b5fab8052498a",
        "_cell_guid": "79c7e3d0-c299-4dcb-8224-4455121ee9b0",
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Let us see the classes present in the dataset:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "data_dir  = '/kaggle/input/garbage-classification/Garbage classification/Garbage classification'\n\nclasses = os.listdir(data_dir)\nprint(classes)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "## Transformations:",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "Now, let's apply transformations to the dataset and import it for use.",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "from torchvision.datasets import ImageFolder\nimport torchvision.transforms as transforms\n\ntransformations = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor()])\n\ndataset = ImageFolder(data_dir, transform = transformations)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Let's create a helper function to see the image and its corresponding label:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "import matplotlib.pyplot as plt\n%matplotlib inline\n\ndef show_sample(img, label):\n    print(\"Label:\", dataset.classes[label], \"(Class No: \"+ str(label) + \")\")\n    plt.imshow(img.permute(1, 2, 0))",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "img, label = dataset[12]\nshow_sample(img, label)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Loading and Splitting Data:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "random_seed = 42\ntorch.manual_seed(random_seed)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "We'll split the dataset into training, validation and test sets:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "train_ds, val_ds, test_ds = random_split(dataset, [1593, 176, 758])\nlen(train_ds), len(val_ds), len(test_ds)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "from torch.utils.data.dataloader import DataLoader\nbatch_size = 32",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Now, we'll create training and validation dataloaders using `DataLoader`.",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "train_dl = DataLoader(train_ds, batch_size, shuffle = True, num_workers = 4, pin_memory = True)\nval_dl = DataLoader(val_ds, batch_size*2, num_workers = 4, pin_memory = True)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "This is a helper function to visualize batches:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "from torchvision.utils import make_grid\n\ndef show_batch(dl):\n    for images, labels in dl:\n        fig, ax = plt.subplots(figsize=(12, 6))\n        ax.set_xticks([])\n        ax.set_yticks([])\n        ax.imshow(make_grid(images, nrow = 16).permute(1, 2, 0))\n        break",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "show_batch(train_dl)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Model Base:",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "Let's create the model base:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "def accuracy(outputs, labels):\n    _, preds = torch.max(outputs, dim=1)\n    return torch.tensor(torch.sum(preds == labels).item() / len(preds))\n\nclass ImageClassificationBase(nn.Module):\n    def training_step(self, batch):\n        images, labels = batch \n        out = self(images)                  # Generate predictions\n        loss = F.cross_entropy(out, labels) # Calculate loss\n        return loss\n    \n    def validation_step(self, batch):\n        images, labels = batch \n        out = self(images)                    # Generate predictions\n        loss = F.cross_entropy(out, labels)   # Calculate loss\n        acc = accuracy(out, labels)           # Calculate accuracy\n        return {'val_loss': loss.detach(), 'val_acc': acc}\n        \n    def validation_epoch_end(self, outputs):\n        batch_losses = [x['val_loss'] for x in outputs]\n        epoch_loss = torch.stack(batch_losses).mean()   # Combine losses\n        batch_accs = [x['val_acc'] for x in outputs]\n        epoch_acc = torch.stack(batch_accs).mean()      # Combine accuracies\n        return {'val_loss': epoch_loss.item(), 'val_acc': epoch_acc.item()}\n    \n    def epoch_end(self, epoch, result):\n        print(\"Epoch {}: train_loss: {:.4f}, val_loss: {:.4f}, val_acc: {:.4f}\".format(\n            epoch+1, result['train_loss'], result['val_loss'], result['val_acc']))",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "We'll be using ResNet50 for classifying images:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "class ResNet(ImageClassificationBase):\n    def __init__(self):\n        super().__init__()\n        # Use a pretrained model\n        self.network = models.resnet50(pretrained=True)\n        # Replace last layer\n        num_ftrs = self.network.fc.in_features\n        self.network.fc = nn.Linear(num_ftrs, len(dataset.classes))\n    \n    def forward(self, xb):\n        return torch.sigmoid(self.network(xb))\n\nmodel = ResNet()",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "## Porting to GPU:",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "GPUs tend to perform faster calculations than CPU. Let's take this advantage and use GPU for computation:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "def get_default_device():\n    \"\"\"Pick GPU if available, else CPU\"\"\"\n    if torch.cuda.is_available():\n        return torch.device('cuda')\n    else:\n        return torch.device('cpu')\n    \ndef to_device(data, device):\n    \"\"\"Move tensor(s) to chosen device\"\"\"\n    if isinstance(data, (list,tuple)):\n        return [to_device(x, device) for x in data]\n    return data.to(device, non_blocking=True)\n\nclass DeviceDataLoader():\n    \"\"\"Wrap a dataloader to move data to a device\"\"\"\n    def __init__(self, dl, device):\n        self.dl = dl\n        self.device = device\n        \n    def __iter__(self):\n        \"\"\"Yield a batch of data after moving it to device\"\"\"\n        for b in self.dl: \n            yield to_device(b, self.device)\n\n    def __len__(self):\n        \"\"\"Number of batches\"\"\"\n        return len(self.dl)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "device = get_default_device()\ndevice",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "train_dl = DeviceDataLoader(train_dl, device)\nval_dl = DeviceDataLoader(val_dl, device)\nto_device(model, device)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Training the Model:",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "This is the function for fitting the model.",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "@torch.no_grad()\ndef evaluate(model, val_loader):\n    model.eval()\n    outputs = [model.validation_step(batch) for batch in val_loader]\n    return model.validation_epoch_end(outputs)\n\ndef fit(epochs, lr, model, train_loader, val_loader, opt_func=torch.optim.SGD):\n    history = []\n    optimizer = opt_func(model.parameters(), lr)\n    for epoch in range(epochs):\n        # Training Phase \n        model.train()\n        train_losses = []\n        for batch in train_loader:\n            loss = model.training_step(batch)\n            train_losses.append(loss)\n            loss.backward()\n            optimizer.step()\n            optimizer.zero_grad()\n        # Validation phase\n        result = evaluate(model, val_loader)\n        result['train_loss'] = torch.stack(train_losses).mean().item()\n        model.epoch_end(epoch, result)\n        history.append(result)\n    return history",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "model = to_device(ResNet(), device)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "evaluate(model, val_dl)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Let's start training the model:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "num_epochs = 8\nopt_func = torch.optim.Adam\nlr = 5.5e-5\n\nhistory = fit(num_epochs, lr, model, train_dl, val_dl, opt_func)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "def plot_accuracies(history):\n    accuracies = [x['val_acc'] for x in history]\n    plt.plot(accuracies, '-x')\n    plt.xlabel('epoch')\n    plt.ylabel('accuracy')\n    plt.title('Accuracy vs. No. of epochs');\n\nplot_accuracies(history)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "def plot_losses(history):\n    train_losses = [x.get('train_loss') for x in history]\n    val_losses = [x['val_loss'] for x in history]\n    plt.plot(train_losses, '-bx')\n    plt.plot(val_losses, '-rx')\n    plt.xlabel('epoch')\n    plt.ylabel('loss')\n    plt.legend(['Training', 'Validation'])\n    plt.title('Loss vs. No. of epochs');\n\nplot_losses(history)",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Visualizing Predictions:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "def predict_image(img, model):\n    # Convert to a batch of 1\n    xb = to_device(img.unsqueeze(0), device)\n    # Get predictions from model\n    yb = model(xb)\n    # Pick index with highest probability\n    prob, preds  = torch.max(yb, dim=1)\n    # Retrieve the class label\n    return dataset.classes[preds[0].item()]",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Let us see the model's predictions on the test dataset:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "img, label = test_ds[17]\nplt.imshow(img.permute(1, 2, 0))\nprint('Label:', dataset.classes[label], ', Predicted:', predict_image(img, model))",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "img, label = test_ds[23]\nplt.imshow(img.permute(1, 2, 0))\nprint('Label:', dataset.classes[label], ', Predicted:', predict_image(img, model))",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "img, label = test_ds[51]\nplt.imshow(img.permute(1, 2, 0))\nprint('Label:', dataset.classes[label], ', Predicted:', predict_image(img, model))",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Predicting External Images:",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "Let's now test with external images.\n\nI'll use `urllib` for downloading external images.",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "import urllib.request\nurllib.request.urlretrieve(\"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fengage.vic.gov.au%2Fapplication%2Ffiles%2F1415%2F0596%2F9236%2FDSC_0026.JPG&f=1&nofb=1\", \"plastic.jpg\")\nurllib.request.urlretrieve(\"https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fi.ebayimg.com%2Fimages%2Fi%2F291536274730-0-1%2Fs-l1000.jpg&f=1&nofb=1\", \"cardboard.jpg\")    \nurllib.request.urlretrieve(\"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.2F0uH6BguQMctAYEJ-s-1gHaHb%26pid%3DApi&f=1\", \"cans.jpg\") \nurllib.request.urlretrieve(\"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftinytrashcan.com%2Fwp-content%2Fuploads%2F2018%2F08%2Ftiny-trash-can-bulk-wine-bottle.jpg&f=1&nofb=1\", \"wine-trash.jpg\")\nurllib.request.urlretrieve(\"http://ourauckland.aucklandcouncil.govt.nz/media/7418/38-94320.jpg\", \"paper-trash.jpg\")",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "Let us load the model. You can load an external pre-trained model too!",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "loaded_model = model",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "This function takes the image's name and prints the predictions:",
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": "from PIL import Image\nfrom pathlib import Path\n\ndef predict_external_image(image_name):\n    image = Image.open(Path('./' + image_name))\n\n    example_image = transformations(image)\n    plt.imshow(example_image.permute(1, 2, 0))\n    print(\"The image resembles\", predict_image(example_image, loaded_model) + \".\")",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "predict_external_image('cans.jpg')",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "predict_external_image('cardboard.jpg')",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "predict_external_image('plastic.jpg')",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "predict_external_image('wine-trash.jpg')",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": "predict_external_image('paper-trash.jpg')",
      "metadata": {
        "trusted": true
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": "# Conclusion:\n\nOur model is able to classify garbage with **95% accuracy**!\n\nIt's great to see the model's predictions on the test set. It works pretty good on external images too!\n\nYou can try experimenting with more images and see the results!",
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": "### If you liked the kernel, don't forget to show some appreciation :)",
      "metadata": {}
    }
  ]
}