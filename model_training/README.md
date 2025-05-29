# Model Training

While this workshop focuses on deployed code and inference of Machine Learning models, it is not the only place where we can understand the energy consumption of our machine learning systems. For example, we can also measure the energy consumption of training our models.

This directory contains a simple example of how to train a model and measure its energy consumption. The example uses the `codecarbon` package to measure the energy consumption of training a transformers model. This has been conveniently built into the Hugging Face `Trainer` class, so we can use it with minimal changes to our code.


We will **not** have time to go over this in the workshop, but we have included it so you have an idea how this works (and how easy it is to integrate!).


### Integrating Codecarbon in the transformers trainer

The Codecarbon library can be integrated into the Huggingface transformers trainer to track the carbon emissions of your training jobs. This is done by including codecarbon in the `report_to` argument of the Trainer class, in fact by default this is set to `all` meaning it's included by default. 

``` python
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    save_steps=10_000,
    save_total_limit=2,
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    report_to="codecarbon",
)
```

This will track the emissions during training and save them to a CSV file in the output directory. You can then use the Codecarbon library to visualize the emissions as we did before. For more information on displaying your carbon emissions see the [Hugging Face documentation]().

# Running a Jupyter environment to run the Notebook

A poetry environment is provided to run the training notebook. You can install the dependencies with:

```bash
poetry install
```

Then, you can run the Jupyter notebook environment with:

```bash
poetry run jupyter notebook train_carbon_intensity_prediction_model.ipynb
```

